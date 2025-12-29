# ============================================
# Nova IR Core
# --------------------------------------------
# This file defines the full Nova Intermediate Representation (IR):
#
#   - OpCode: complete instruction set (broad, not minimal)
#   - IRConst: literal constant values
#   - IRTemp: temporary SSA-like values
#   - IRInstruction: a single IR operation
#   - IRBlock: a basic block containing IR instructions
#   - IRFunction: a function consisting of blocks and temps
#   - IRModule: a module containing functions
#
# This IR is designed to be consumed by:
#   - the Nova VM
#   - the LLVM backend
#   - future optimizers and analyzers
# ============================================

from enum import Enum, auto


# --------------------------------------------
# OpCode – Full Nova Instruction Set
# --------------------------------------------

class OpCode(Enum):
    # ----------------------------------------
    # Constants & Variables
    # ----------------------------------------
    LOAD_CONST = auto()      # dest, value
    LOAD_VAR   = auto()      # dest, var_name
    STORE_VAR  = auto()      # var_name, src

    # ----------------------------------------
    # Arithmetic
    # ----------------------------------------
    ADD = auto()             # dest, a, b
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    POW = auto()
    NEG = auto()             # dest, a

    # ----------------------------------------
    # Comparison (produces boolean)
    # ----------------------------------------
    EQ = auto()              # dest, a, b
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # ----------------------------------------
    # Logic
    # ----------------------------------------
    AND = auto()             # dest, a, b
    OR  = auto()
    NOT = auto()             # dest, a

    # ----------------------------------------
    # Control Flow
    # ----------------------------------------
    JUMP          = auto()   # label_name
    JUMP_IF_TRUE  = auto()   # cond_temp, label_name
    JUMP_IF_FALSE = auto()   # cond_temp, label_name
    # Labels are represented as IRBlocks, so no LABEL opcode is needed.

    # ----------------------------------------
    # Functions
    # ----------------------------------------
    CALL   = auto()          # dest, func_name, arg_temps[]
    RETURN = auto()          # value_temp or None

    # ----------------------------------------
    # Iterators (for-loops)
    # ----------------------------------------
    MAKE_ITER     = auto()   # dest_iter, iterable_temp
    ITER_HAS_NEXT = auto()   # dest_bool, iter_temp
    ITER_NEXT     = auto()   # dest_value, iter_temp

    # ----------------------------------------
    # Lists / Arrays
    # ----------------------------------------
    LIST_NEW    = auto()     # dest_list
    LIST_APPEND = auto()     # list_temp, value_temp
    LIST_GET    = auto()     # dest, list_temp, index_temp
    LIST_SET    = auto()     # list_temp, index_temp, value_temp
    LIST_LEN    = auto()     # dest, list_temp

    # ----------------------------------------
    # Maps / Dictionaries
    # ----------------------------------------
    MAP_NEW     = auto()     # dest_map
    MAP_GET     = auto()     # dest, map_temp, key_temp
    MAP_SET     = auto()     # map_temp, key_temp, value_temp
    MAP_HAS_KEY = auto()     # dest_bool, map_temp, key_temp
    MAP_KEYS    = auto()     # dest_list, map_temp
    MAP_VALUES  = auto()     # dest_list, map_temp

    # ----------------------------------------
    # Strings
    # ----------------------------------------
    STR_CONCAT = auto()      # dest, a_temp, b_temp
    STR_LEN    = auto()      # dest, str_temp
    STR_GET    = auto()      # dest, str_temp, index_temp

    # ----------------------------------------
    # Modules / Native Interop
    # ----------------------------------------
    USE_MODULE    = auto()   # module_name (IRConst)
    IMPORT_MODULE = auto()   # dest_module, module_name
    IMPORT_SYMBOL = auto()   # dest, module_temp, symbol_name
    NATIVE_CALL   = auto()   # dest, native_name, arg_temps[]

    # ----------------------------------------
    # Debug / System
    # ----------------------------------------
    PRINT = auto()           # value_temp or IRConst
    DEBUG = auto()           # value_temp
    NOP   = auto()
    HALT  = auto()


# --------------------------------------------
# IR Values
# --------------------------------------------

class IRConst:
    """Represents a literal constant value in the IR (int, string, bool, etc.)."""

    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"IRConst({self.value!r})"


class IRTemp:
    """Represents a temporary SSA-like value produced by an instruction."""

    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"%{self.name}"


# --------------------------------------------
# IRInstruction
# --------------------------------------------

class IRInstruction:
    """
    Represents a single IR instruction.

    Attributes:
        opcode: OpCode or string (transition compatibility)
        operands: list of IRConst, IRTemp, or strings
        result: IRTemp or None
    """

    __slots__ = ("opcode", "operands", "result")

    def __init__(self, opcode, operands=None, result=None):
        self.opcode = opcode
        self.operands = operands or []
        self.result = result

    def __repr__(self):
        op_name = self.opcode.name if isinstance(self.opcode, OpCode) else str(self.opcode)
        ops = ", ".join(repr(o) for o in self.operands)
        if self.result is not None:
            return f"{self.result} = {op_name}({ops})"
        return f"{op_name}({ops})"


# --------------------------------------------
# IRBlock
# --------------------------------------------

class IRBlock:
    """A basic block containing a sequence of IR instructions."""

    __slots__ = ("name", "instructions")

    def __init__(self, name: str):
        self.name = name
        self.instructions = []

    def add(self, instr: IRInstruction):
        self.instructions.append(instr)

    def __repr__(self):
        lines = [f"{self.name}:"]
        for instr in self.instructions:
            lines.append(f"  {instr}")
        return "\n".join(lines)


# --------------------------------------------
# IRFunction
# --------------------------------------------

class IRFunction:
    """
    Represents a function in the IR.

    Attributes:
        name: function name
        params: list of parameter names
        blocks: list of IRBlock
        _temp_counter: counter for generating unique IRTemp names
    """

    __slots__ = ("name", "params", "blocks", "_temp_counter")

    def __init__(self, name: str, params=None):
        self.name = name
        self.params = params or []
        self.blocks = []
        self._temp_counter = 0

    def new_block(self, name: str) -> IRBlock:
        block = IRBlock(name)
        self.blocks.append(block)
        return block

    def new_temp(self) -> IRTemp:
        tname = f"t{self._temp_counter}"
        self._temp_counter += 1
        return IRTemp(tname)

    def __repr__(self):
        lines = [f"func {self.name}({', '.join(self.params)})"]
        for block in self.blocks:
            lines.append(repr(block))
        return "\n".join(lines)


# --------------------------------------------
# IRModule
# --------------------------------------------

class IRModule:
    """Represents a Nova module containing multiple IR functions."""

    __slots__ = ("name", "functions")

    def __init__(self, name: str):
        self.name = name
        self.functions = []

    def add_function(self, func: IRFunction):
        self.functions.append(func)

    def __repr__(self):
        lines = [f"module {self.name}"]
        for f in self.functions:
            lines.append(repr(f))
        return "\n\n".join(lines)
