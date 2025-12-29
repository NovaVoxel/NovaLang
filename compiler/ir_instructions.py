# compiler/ir_instructions.py

from enum import Enum, auto


class OpCode(Enum):
    LOAD_CONST = auto()
    LOAD_VAR = auto()
    STORE_VAR = auto()
    BINARY_ADD = auto()
    BINARY_SUB = auto()
    BINARY_MUL = auto()
    BINARY_DIV = auto()

    JUMP = auto()
    JUMP_IF_FALSE = auto()

    MAKE_ITER = auto()        # iter = iter(expr)
    ITER_HAS_NEXT = auto()    # bool = iter_has_next(iter)
    ITER_NEXT = auto()        # value = iter_next(iter)

    # ggf. weitere Opcodes...


class IRInstruction:
    def __init__(self, op: OpCode, *args):
        self.op = op
        self.args = list(args)

    def __repr__(self):
        return f"IR({self.op}, {', '.join(map(repr, self.args))})"
