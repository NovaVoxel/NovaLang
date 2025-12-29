# ============================================
# Nova IR Builder
# Converts AST nodes into IRModule + IRFunctions + IRInstructions
# ============================================

from .ast import FunctionDef, UseStmt, Block
from .ir import (
    IRModule,
    IRFunction,
    IRInstruction,
    IRConst,
    IRTemp
)


class IRBuilder:
    def __init__(self):
        self.module = IRModule("nova_module")
        self.current_function = None
        self.current_block = None

    # ----------------------------------------
    # Helpers
    # ----------------------------------------

    def new_block(self, name):
        block = self.current_function.new_block(name)
        self.current_block = block
        return block

    def emit(self, opcode, operands=None, result=False):
        """Emit an instruction into the current block."""
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
    # Main entry
    # ----------------------------------------

    def build(self, ast):
        for node in ast:
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

        # Example: print function name
        self.emit("print", [IRConst(f"Hello from {node.name}")])

        # Build body
        self.build_block(node.body)

        # Ensure function ends with return
        self.emit("ret")

    # ----------------------------------------
    # Block builder
    # ----------------------------------------

    def build_block(self, block: Block):
        for stmt in block.statements:
            if isinstance(stmt, UseStmt):
                self.build_use(stmt)
            elif isinstance(stmt, FunctionDef):
                # Nested function
                self.build_function(stmt)
            else:
                # Unknown → ignore for now
                pass

    # ----------------------------------------
    # use <module>
    # ----------------------------------------

    def build_use(self, stmt: UseStmt):
        self.emit("use_module", [IRConst(stmt.module)])
