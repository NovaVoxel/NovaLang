# Nova Intermediate Representation (IR) definitions
# This IR is a simplified layer between AST and LLVM IR

class IRInstruction:
    def __init__(self, opcode, operands=None):
        self.opcode = opcode
        self.operands = operands or []

    def __repr__(self):
        return f"{self.opcode} {' '.join(map(str, self.operands))}"

class IRFunction:
    def __init__(self, name):
        self.name = name
        self.instructions = []

    def add(self, instr: IRInstruction):
        self.instructions.append(instr)

    def __repr__(self):
        return f"Function {self.name}:\n" + "\n".join(map(str, self.instructions))

class IRModule:
    def __init__(self, name="nova_module"):
        self.name = name
        self.functions = []

    def add_function(self, func: IRFunction):
        self.functions.append(func)

    def __repr__(self):
        return f"Module {self.name}\n" + "\n".join(map(str, self.functions))
