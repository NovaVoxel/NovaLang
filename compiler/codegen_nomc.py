# ============================================
# Nova LLVM backend with LTO support
# Emits optimized native machine code into .nomc files
# ============================================

from llvmlite import ir, binding

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()


class LLVMBackend:
    def __init__(self):
        self.printf = None
        self.string_cache = {}

    # ----------------------------------------
    # Create or reuse printf declaration
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
    # Create or reuse global string
    # ----------------------------------------
    def get_global_string(self, builder, module, text):
        if text in self.string_cache:
            return self.string_cache[text]

        string = builder.global_string(text, name=f"str_{len(self.string_cache)}")
        self.string_cache[text] = string
        return string

    # ----------------------------------------
    # Lower a single Nova IR instruction
    # ----------------------------------------
    def lower_instruction(self, builder, module, instr):
        op = instr.opcode

        # PRINT_CONST "hello"
        if op == "PRINT_CONST":
            text = instr.operands[0]
            printf = self.get_printf(module)
            gstr = self.get_global_string(builder, module, text + "\n")
            builder.call(printf, [gstr])
            return

        # RETURN or RETURN value
        if op == "RETURN":
            if instr.operands:
                val = instr.operands[0]
                if isinstance(val, int):
                    builder.ret(ir.IntType(32)(val))
                else:
                    raise ValueError("Unsupported return value type")
            else:
                builder.ret(ir.IntType(32)(0))
            return

        # TODO: ADD, SUB, CALL, JUMP, etc.
        print(f"[WARN] Unimplemented IR opcode: {op}")

    # ----------------------------------------
    # Lower a Nova IR function into LLVM IR
    # ----------------------------------------
    def lower_function(self, module, func):
        func_type = ir.FunctionType(ir.IntType(32), [])
        llvm_func = ir.Function(module, func_type, name=func.name)

        entry = llvm_func.append_basic_block("entry")
        builder = ir.IRBuilder(entry)

        # Lower all blocks + instructions
        for block in func.blocks:
            for instr in block.instructions:
                self.lower_instruction(builder, module, instr)

        # Ensure function ends with return
        if not builder.block.is_terminated:
            builder.ret(ir.IntType(32)(0))

    # ----------------------------------------
    # Build LLVM module from Nova IR module
    # ----------------------------------------
    def build_llvm_module(self, ir_module):
        llvm_module = ir.Module(name=ir_module.name)

        for func in ir_module.functions:
            self.lower_function(llvm_module, func)

        return llvm_module

    # ----------------------------------------
    # Emit optimized native object file (.nomc)
    # ----------------------------------------
    def emit_nomc(self, llvm_module, output):
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine(opt=3)

        # LTO-ready object emission
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
