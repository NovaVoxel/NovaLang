# ============================================
# Nova IR Builder
# --------------------------------------------
# Converts AST nodes into:
#   - IRModule
#   - IRFunction
#   - IRBlocks
#   - IRInstructions
#
# This builder produces a *broad* IR suitable
# for lowering directly into LLVM IR.
#
# Supports:
#   - Function definitions
#   - Blocks
#   - Variable assignment
#   - Expressions
#   - If / While
#   - Python-style for-loops (without "in")
#   - Module imports
#   - Return statements
#
# No VM. No bytecode. This IR is intended
# exclusively for LLVM lowering → .nomc.
# ============================================

from .ir import (
    IRModule,
    IRFunction,
    IRBlock,
    IRInstruction,
    IRConst,
    IRTemp,
    OpCode
)

from .nova_ast import (
    FunctionDef,
    Block,
    UseStmt,
    VarAssign,
    VarRef,
    NumberLiteral,
    StringLiteral,
    BinaryOp,
    CallExpr,
    IfStmt,
    WhileStmt,
    ForEachStmt,
    ReturnStmt
)


class IRBuilder:
    def __init__(self):
        self.module = IRModule("nova_module")
        self.current_function = None
        self.current_block = None

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    def new_block(self, name: str) -> IRBlock:
        block = self.current_function.new_block(name)
        self.current_block = block
        return block

    def emit(self, opcode, operands=None, result=False):
        """Emit an IR instruction into the current block."""
        operands = operands or []

        if result:
            temp = self.current_function.new_temp()
            instr = IRInstruction(opcode, operands, result=temp)
            self.current_block.add(instr)
            return temp

        instr = IRInstruction(opcode, operands)
        self.current_block.add(instr)
        return None

    # ----------------------------------------
    # Entry point
    # ----------------------------------------

    def build(self, ast_list):
        for node in ast_list:
            if isinstance(node, FunctionDef):
                self.build_function(node)
        return self.module

    # ----------------------------------------
    # Function builder
    # ----------------------------------------

    def build_function(self, node: FunctionDef):
        func = IRFunction(node.name, params=node.params)
        self.module.add_function(func)

        self.current_function = func
        self.new_block("entry")

        # Build function body
        self.build_block(node.body)

        # Ensure function ends with return
        if not self.current_block.instructions or \
           self.current_block.instructions[-1].opcode != OpCode.RETURN:
            self.emit(OpCode.RETURN)

    # ----------------------------------------
    # Block builder
    # ----------------------------------------

    def build_block(self, block: Block):
        for stmt in block.statements:
            self.build_statement(stmt)

    # ----------------------------------------
    # Statement dispatcher
    # ----------------------------------------

    def build_statement(self, stmt):
        if isinstance(stmt, UseStmt):
            return self.emit(OpCode.USE_MODULE, [IRConst(stmt.module)])

        if isinstance(stmt, VarAssign):
            value = self.build_expression(stmt.value)
            return self.emit(OpCode.STORE_VAR, [stmt.name, value])

        if isinstance(stmt, IfStmt):
            return self.build_if(stmt)

        if isinstance(stmt, WhileStmt):
            return self.build_while(stmt)

        if isinstance(stmt, ForEachStmt):
            return self.build_for_each(stmt)

        if isinstance(stmt, ReturnStmt):
            return self.build_return(stmt)

        # Expression as statement
        if hasattr(stmt, "expr"):
            self.build_expression(stmt.expr)
            return

        # Unknown → ignore
        return

    # ----------------------------------------
    # If statement
    # ----------------------------------------

    def build_if(self, stmt: IfStmt):
        cond = self.build_expression(stmt.condition)

        then_block = self.new_block("if_then")
        else_block = self.new_block("if_else") if stmt.else_block else None
        end_block = self.new_block("if_end")

        # Jump based on condition
        self.emit(OpCode.JUMP_IF_FALSE, [cond, else_block.name if else_block else end_block.name])

        # THEN
        self.current_block = then_block
        self.build_block(stmt.then_block)
        self.emit(OpCode.JUMP, [end_block.name])

        # ELSE
        if stmt.else_block:
            self.current_block = else_block
            self.build_block(stmt.else_block)
            self.emit(OpCode.JUMP, [end_block.name])

        # END
        self.current_block = end_block

    # ----------------------------------------
    # While loop
    # ----------------------------------------

    def build_while(self, stmt: WhileStmt):
        start = self.new_block("while_start")
        cond_block = self.new_block("while_cond")
        body_block = self.new_block("while_body")
        end_block = self.new_block("while_end")

        # Jump to condition
        self.emit(OpCode.JUMP, [cond_block.name])

        # Condition
        self.current_block = cond_block
        cond = self.build_expression(stmt.condition)
        self.emit(OpCode.JUMP_IF_FALSE, [cond, end_block.name])
        self.emit(OpCode.JUMP, [body_block.name])

        # Body
        self.current_block = body_block
        self.build_block(stmt.body)
        self.emit(OpCode.JUMP, [cond_block.name])

        # End
        self.current_block = end_block

    # ----------------------------------------
    # Python-style for-loop (no "in")
    # for i range(0,10) { ... }
    # for x list { ... }
    # ----------------------------------------

    def build_for_each(self, stmt: ForEachStmt):
        iterable = self.build_expression(stmt.iterable)

        iter_temp = self.emit(OpCode.MAKE_ITER, [iterable], result=True)

        start = self.new_block("for_start")
        cond_block = self.new_block("for_cond")
        body_block = self.new_block("for_body")
        end_block = self.new_block("for_end")

        # Jump to condition
        self.emit(OpCode.JUMP, [cond_block.name])

        # Condition
        self.current_block = cond_block
        has_next = self.emit(OpCode.ITER_HAS_NEXT, [iter_temp], result=True)
        self.emit(OpCode.JUMP_IF_FALSE, [has_next, end_block.name])
        self.emit(OpCode.JUMP, [body_block.name])

        # Body
        self.current_block = body_block
        value = self.emit(OpCode.ITER_NEXT, [iter_temp], result=True)
        self.emit(OpCode.STORE_VAR, [stmt.var_name, value])
        self.build_block(stmt.body)
        self.emit(OpCode.JUMP, [cond_block.name])

        # End
        self.current_block = end_block

    # ----------------------------------------
    # Return
    # ----------------------------------------

    def build_return(self, stmt: ReturnStmt):
        if stmt.value:
            val = self.build_expression(stmt.value)
            self.emit(OpCode.RETURN, [val])
        else:
            self.emit(OpCode.RETURN)

    # ----------------------------------------
    # Expression builder
    # ----------------------------------------

    def build_expression(self, expr):
        if isinstance(expr, NumberLiteral):
            return self.emit(OpCode.LOAD_CONST, [IRConst(expr.value)], result=True)

        if isinstance(expr, StringLiteral):
            return self.emit(OpCode.LOAD_CONST, [IRConst(expr.value)], result=True)

        if isinstance(expr, VarRef):
            return self.emit(OpCode.LOAD_VAR, [expr.name], result=True)

        if isinstance(expr, BinaryOp):
            left = self.build_expression(expr.left)
            right = self.build_expression(expr.right)
            opcode = {
                "+": OpCode.ADD,
                "-": OpCode.SUB,
                "*": OpCode.MUL,
                "/": OpCode.DIV,
                "%": OpCode.MOD,
                "==": OpCode.EQ,
                "!="": OpCode.NE,
                "<": OpCode.LT,
                "<=": OpCode.LE,
                ">": OpCode.GT,
                ">=": OpCode.GE,
            }[expr.op]
            return self.emit(opcode, [left, right], result=True)

        if isinstance(expr, CallExpr):
            args = [self.build_expression(a) for a in expr.args]
            return self.emit(OpCode.CALL, [expr.func_name, args], result=True)

        raise RuntimeError(f"Unknown expression node: {expr}")
