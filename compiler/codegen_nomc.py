# ============================================
# Nova LLVM backend with LTO support
# Emits optimized native machine code into .nomc files
# ============================================

from llvmlite import ir, binding
from .ir import IRConst, IRTemp, OpCode

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()


# ============================================
# LLVM Backend
# ============================================

class LLVMBackend:
    def __init__(self):
        self.printf = None
        self.string_cache = {}
        self.value_map = {}       # IRTemp.name -> LLVM value
        self.var_map = {}         # var_name -> LLVM pointer
        self.block_map = {}       # IRBlock.name -> LLVM BasicBlock
        self.current_function = None

    # ----------------------------------------
    # printf declaration
    # ----------------------------------------
    def get_printf(self, module):
        if self.printf:
            return self.printf

        printf_ty = ir.FunctionType(
            ir.IntType(32),
            [ir.PointerType(ir.IntType(8))],
            var_arg=True
        )
        self.printf = ir.Function(module, printf_ty, name="printf")
        return self.printf

    # ----------------------------------------
    # Global string
    # ----------------------------------------
    def get_global_string(self, module, text):
        if text in self.string_cache:
            return self.string_cache[text]

        arr = bytearray(text.encode("utf8")) + b"\00"
        string_ty = ir.ArrayType(ir.IntType(8), len(arr))
        global_var = ir.GlobalVariable(module, string_ty, name=f".str_{len(self.string_cache)}")
        global_var.linkage = "internal"
        global_var.global_constant = True
        global_var.initializer = ir.Constant(string_ty, arr)

        ptr = global_var.bitcast(ir.IntType(8).as_pointer())
        self.string_cache[text] = ptr
        return ptr

    # ----------------------------------------
    # Convert IR operand → LLVM value
    # ----------------------------------------
    def to_llvm(self, builder, module, operand):
        if isinstance(operand, IRConst):
            if isinstance(operand.value, int):
                return ir.IntType(32)(operand.value)
            if isinstance(operand.value, str):
                return self.get_global_string(module, operand.value)
            raise ValueError("Unsupported IRConst type")

        if isinstance(operand, IRTemp):
            return self.value_map[operand.name]

        if isinstance(operand, str):
            # variable name → load from alloca
            if operand in self.var_map:
                return builder.load(self.var_map[operand])
            raise ValueError(f"Unknown variable: {operand}")

        return operand

    # ----------------------------------------
    # Bind result temp
    # ----------------------------------------
    def bind_result(self, instr, llvm_val):
        if instr.result:
            self.value_map[instr.result.name] = llvm_val

    # ----------------------------------------
    # Runtime helper declarations
    # ----------------------------------------
    def declare_runtime(self, module):
        # Example runtime functions (you can implement them in C later)
        def declare(name, ret, args):
            fnty = ir.FunctionType(ret, args)
            return ir.Function(module, fnty, name=name)

        self.rt_list_new = declare("nova_list_new", ir.IntType(8).as_pointer(), [])
        self.rt_list_append = declare("nova_list_append", ir.VoidType(),
                                      [ir.IntType(8).as_pointer(), ir.IntType(32)])
        self.rt_iter_make = declare("nova_iter_make", ir.IntType(8).as_pointer(),
                                    [ir.IntType(8).as_pointer()])
        self.rt_iter_has_next = declare("nova_iter_has_next", ir.IntType(1),
                                        [ir.IntType(8).as_pointer()])
        self.rt_iter_next = declare("nova_iter_next", ir.IntType(32),
                                    [ir.IntType(8).as_pointer()])

    # ----------------------------------------
    # Lower a single IR instruction
    # ----------------------------------------
    def lower_instruction(self, builder, module, instr):
        op = instr.opcode

        # ----------------------------------------
        # PRINT
        # ----------------------------------------
        if op == OpCode.PRINT:
            val = self.to_llvm(builder, module, instr.operands[0])
            printf = self.get_printf(module)

            if isinstance(val.type, ir.IntType):
                fmt = self.get_global_string(module, "%d\n")
                builder.call(printf, [fmt, val])
            else:
                builder.call(printf, [val])
            return

        # ----------------------------------------
        # LOAD_CONST
        # ----------------------------------------
        if op == OpCode.LOAD_CONST:
            llvm_val = self.to_llvm(builder, module, instr.operands[0])
            self.bind_result(instr, llvm_val)
            return

        # ----------------------------------------
        # LOAD_VAR
        # ----------------------------------------
        if op == OpCode.LOAD_VAR:
            var_name = instr.operands[0]
            llvm_val = builder.load(self.var_map[var_name])
            self.bind_result(instr, llvm_val)
            return

        # ----------------------------------------
        # STORE_VAR
        # ----------------------------------------
        if op == OpCode.STORE_VAR:
            var_name, src = instr.operands
            llvm_val = self.to_llvm(builder, module, src)
            if var_name not in self.var_map:
                self.var_map[var_name] = builder.alloca(ir.IntType(32))
            builder.store(llvm_val, self.var_map[var_name])
            return

        # ----------------------------------------
        # Arithmetic
        # ----------------------------------------
        if op in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD):
            lhs = self.to_llvm(builder, module, instr.operands[0])
            rhs = self.to_llvm(builder, module, instr.operands[1])

            if op == OpCode.ADD:
                res = builder.add(lhs, rhs)
            elif op == OpCode.SUB:
                res = builder.sub(lhs, rhs)
            elif op == OpCode.MUL:
                res = builder.mul(lhs, rhs)
            elif op == OpCode.DIV:
                res = builder.sdiv(lhs, rhs)
            elif op == OpCode.MOD:
                res = builder.srem(lhs, rhs)

            self.bind_result(instr, res)
            return

        # ----------------------------------------
        # Comparison
        # ----------------------------------------
        if op in (OpCode.EQ, OpCode.NE, OpCode.LT, OpCode.LE, OpCode.GT, OpCode.GE):
            lhs = self.to_llvm(builder, module, instr.operands[0])
            rhs = self.to_llvm(builder, module, instr.operands[1])

            cmp_map = {
                OpCode.EQ: "==",
                OpCode.NE: "!=",
                OpCode.LT: "<",
                OpCode.LE: "<=",
                OpCode.GT: ">",
                OpCode.GE: ">=",
            }

            pred = cmp_map[op]
            res = builder.icmp_signed(pred, lhs, rhs)
            self.bind_result(instr, res)
            return

        # ----------------------------------------
        # Control Flow
        # ----------------------------------------
        if op == OpCode.JUMP:
            label = instr.operands[0]
            builder.branch(self.block_map[label])
            return

        if op == OpCode.JUMP_IF_FALSE:
            cond = self.to_llvm(builder, module, instr.operands[0])
            label = instr.operands[1]
            builder.cbranch(cond, self.block_map[label], builder.block)
            return

        # ----------------------------------------
        # RETURN
        # ----------------------------------------
        if op == OpCode.RETURN:
            if instr.operands:
                val = self.to_llvm(builder, module, instr.operands[0])
                builder.ret(val)
            else:
                builder.ret(ir.IntType(32)(0))
            return

        # ----------------------------------------
        # Iterators
        # ----------------------------------------
        if op == OpCode.MAKE_ITER:
            iterable = self.to_llvm(builder, module, instr.operands[0])
            res = builder.call(self.rt_iter_make, [iterable])
            self.bind_result(instr, res)
            return

        if op == OpCode.ITER_HAS_NEXT:
            it = self.to_llvm(builder, module, instr.operands[0])
            res = builder.call(self.rt_iter_has_next, [it])
            self.bind_result(instr, res)
            return

        if op == OpCode.ITER_NEXT:
            it = self.to_llvm(builder, module, instr.operands[0])
            res = builder.call(self.rt_iter_next, [it])
            self.bind_result(instr, res)
            return

        print(f"[WARN] Unimplemented IR opcode: {op}")

    # ----------------------------------------
    # Lower a function
    # ----------------------------------------
    def lower_function(self, module, func):
        func_ty = ir.FunctionType(ir.IntType(32), [])
        llvm_func = ir.Function(module, func_ty, name=func.name)
        self.current_function = llvm_func

        # Create LLVM blocks for each IRBlock
        self.block_map = {
            block.name: llvm_func.append_basic_block(block.name)
            for block in func.blocks
        }

        # Reset variable maps
        self.value_map = {}
        self.var_map = {}

        # Lower blocks
        for block in func.blocks:
            builder = ir.IRBuilder(self.block_map[block.name])
            for instr in block.instructions:
                self.lower_instruction(builder, module, instr)

            # Ensure block ends with a terminator
            if not builder.block.is_terminated:
                builder.ret(ir.IntType(32)(0))

    # ----------------------------------------
    # Build LLVM module
    # ----------------------------------------
    def build_llvm_module(self, ir_module):
        llvm_module = ir.Module(name=ir_module.name)
        self.declare_runtime(llvm_module)

        for func in ir_module.functions:
            self.lower_function(llvm_module, func)

        return llvm_module

    # ----------------------------------------
    # Emit .nomc
    # ----------------------------------------
    def emit_nomc(self, llvm_module, output):
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine(opt=3)

        obj = target_machine.emit_object(llvm_module)

        with open(output, "wb") as f:
            f.write(obj)

        return output


# ============================================
# Public API
# ============================================

def generate_nomc(ir_module, output="bin/main.nomc"):
    backend = LLVMBackend()
    llvm_module = backend.build_llvm_module(ir_module)
    return backend.emit_nomc(llvm_module, output)
