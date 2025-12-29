# Nova IR Builder
# Converts AST nodes into IRModule with IRFunctions and IRInstructions

from .ast import FunctionDef
from .ir import IRModule, IRFunction, IRInstruction

def build_ir(ast):
    # Create IR module
    module = IRModule(name="nova_module")

    for node in ast:
        if isinstance(node, FunctionDef):
            func = IRFunction(node.name)

            # Example: every function prints "Hello from Nova"
            instr = IRInstruction("PRINT_CONST", [f"Hello from {node.name}"])
            func.add(instr)

            func.add(IRInstruction("RETURN"))
            module.add_function(func)

    return module
