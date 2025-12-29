# Nova LLVM backend code generator
# Translates IRModule → LLVM IR → native object code

from llvmlite import ir, binding

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

def generate_nomc(ir_module, output="bin/main.o"):
    # Create LLVM module
    llvm_module = ir.Module(name=ir_module.name)

    # Define main function
    func_type = ir.FunctionType(ir.IntType(32), [])
    main_func = ir.Function(llvm_module, func_type, name="main")
    block = main_func.append_basic_block(name="entry")
    builder = ir.IRBuilder(block)

    # Example: translate IR instructions
    for func in ir_module.functions:
        for instr in func.instructions:
            if instr.opcode == "PRINT_CONST":
                # Create global string
                text = instr.operands[0]
                hello_str = builder.global_string(text + "\n", name="str")
                # Declare printf
                printf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
                printf = ir.Function(llvm_module, printf_ty, name="printf")
                builder.call(printf, [hello_str])

    builder.ret(ir.IntType(32)(0))

    # Compile to native object code
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine()
    obj = target_machine.emit_object(llvm_module)

    with open(output, "wb") as f:
        f.write(obj)

    return output
