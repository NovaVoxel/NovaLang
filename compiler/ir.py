# ============================================
# Nova Intermediate Representation (IR)
# A structured, extensible IR between AST and LLVM
# ============================================

from dataclasses import dataclass, field
from typing import List, Optional, Union


# ============================================
# Base IR Value
# ============================================

class IRValue:
    """Base class for anything that can be used as an operand."""
    pass


@dataclass
class IRTemp(IRValue):
    """Temporary SSA value (t0, t1, t2...)"""
    name: str

    def __repr__(self):
        return self.name


@dataclass
class IRConst(IRValue):
    """Constant literal value."""
    value: Union[int, float, str]

    def __repr__(self):
        return repr(self.value)


# ============================================
# IR Instruction
# ============================================

@dataclass
class IRInstruction:
    opcode: str
    operands: List[IRValue] = field(default_factory=list)
    result: Optional[IRTemp] = None

    def __repr__(self):
        if self.result:
            return f"{self.result} = {self.opcode} " + " ".join(map(str, self.operands))
        return f"{self.opcode} " + " ".join(map(str, self.operands))


# ============================================
# IR Basic Block
# ============================================

@dataclass
class IRBlock:
    name: str
    instructions: List[IRInstruction] = field(default_factory=list)

    def add(self, instr: IRInstruction):
        self.instructions.append(instr)

    def __repr__(self):
        body = "\n    ".join(map(str, self.instructions))
        return f"{self.name}:\n    {body}"


# ============================================
# IR Function
# ============================================

class IRFunction:
    def __init__(self, name, params=None):
        self.name = name
        self.params = params or []
        self.blocks: List[IRBlock] = []
        self.temp_counter = 0

    def new_temp(self):
        t = IRTemp(f"t{self.temp_counter}")
        self.temp_counter += 1
        return t

    def new_block(self, name):
        block = IRBlock(name)
        self.blocks.append(block)
        return block

    def __repr__(self):
        header = f"Function {self.name}({', '.join(self.params)})"
        blocks = "\n".join(map(str, self.blocks))
        return f"{header}\n{blocks}"


# ============================================
# IR Module
# ============================================

class IRModule:
    def __init__(self, name="nova_module"):
        self.name = name
        self.functions: List[IRFunction] = []

    def add_function(self, func: IRFunction):
        self.functions.append(func)

    def __repr__(self):
        funcs = "\n\n".join(map(str, self.functions))
        return f"Module {self.name}\n\n{funcs}"
