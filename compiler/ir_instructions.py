# compiler/ir_instructions.py
#
# Zentrale Definition der Nova-IR:
#  - OpCode: alle Instruktionen
#  - IRInstruction: eine einzelne Instruktion
#  - IRLabel: Label/Pseudo-Instruktion für Sprünge
#
# Diese IR ist so gedacht, dass:
#  - der IRBuilder sie erzeugt
#  - eine VM oder ein Codegen (z.B. LLVM) sie konsumiert
#  - for/while/if über Jumps + Labels abgebildet werden
#  - Iteratoren (für for) über MAKE_ITER / ITER_HAS_NEXT / ITER_NEXT gehen

from enum import Enum, auto


class OpCode(Enum):
    # ---------------------------------
    # Konstanten & Variablen
    # ---------------------------------
    LOAD_CONST = auto()     # dest, value
    LOAD_VAR   = auto()     # dest, name
    STORE_VAR  = auto()     # name, src

    # ---------------------------------
    # Arithmetik
    # ---------------------------------
    BINARY_ADD = auto()     # dest, a, b
    BINARY_SUB = auto()     # dest, a, b
    BINARY_MUL = auto()     # dest, a, b
    BINARY_DIV = auto()     # dest, a, b
    BINARY_MOD = auto()     # dest, a, b
    BINARY_POW = auto()     # dest, a, b

    # ---------------------------------
    # Vergleich
    # dest ist immer ein bool
    # ---------------------------------
    CMP_EQ = auto()         # dest, a, b
    CMP_NE = auto()         # dest, a, b
    CMP_LT = auto()         # dest, a, b
    CMP_LE = auto()         # dest, a, b
    CMP_GT = auto()         # dest, a, b
    CMP_GE = auto()         # dest, a, b

    # ---------------------------------
    # Logik (boolsche Operationen)
    # ---------------------------------
    LOGIC_AND = auto()      # dest, a, b
    LOGIC_OR  = auto()      # dest, a, b
    LOGIC_NOT = auto()      # dest, a

    # ---------------------------------
    # Control-Flow
    # Labels werden als eigene Klasse IRLabel dargestellt
    # ---------------------------------
    JUMP          = auto()  # label_name
    JUMP_IF_TRUE  = auto()  # cond_temp, label_name
    JUMP_IF_FALSE = auto()  # cond_temp, label_name

    # ---------------------------------
    # Funktionen / Calls
    # ---------------------------------
    CALL   = auto()         # dest, func_ref/name, arg_temps(list)
    RETURN = auto()         # value_temp (oder None für void)

    # Optional: stackbasierte Args, falls du das nutzen willst
    PUSH_ARG = auto()       # value_temp
    POP_ARG  = auto()       # dest

    # ---------------------------------
    # Iteratoren (für for-Schleifen)
    # ---------------------------------
    MAKE_ITER     = auto()  # dest_iter, iterable_temp
    ITER_HAS_NEXT = auto()  # dest_bool, iter_temp
    ITER_NEXT     = auto()  # dest_value, iter_temp

    # ---------------------------------
    # Listen / Arrays
    # ---------------------------------
    LIST_NEW    = auto()    # dest_list
    LIST_APPEND = auto()    # list_temp, value_temp
    LIST_GET    = auto()    # dest, list_temp, index_temp
    LIST_SET    = auto()    # list_temp, index_temp, value_temp
    LIST_LEN    = auto()    # dest, list_temp

    # ---------------------------------
    # Maps / Dictionaries
    # ---------------------------------
    MAP_NEW     = auto()    # dest_map
    MAP_GET     = auto()    # dest, map_temp, key_temp
    MAP_SET     = auto()    # map_temp, key_temp, value_temp
    MAP_HAS_KEY = auto()    # dest_bool, map_temp, key_temp
    MAP_KEYS    = auto()    # dest_list, map_temp
    MAP_VALUES  = auto()    # dest_list, map_temp

    # ---------------------------------
    # Strings
    # ---------------------------------
    STR_CONCAT = auto()     # dest, a_temp, b_temp
    STR_LEN    = auto()     # dest, str_temp
    STR_GET    = auto()     # dest, str_temp, index_temp

    # ---------------------------------
    # Native / Module / Interop
    # ---------------------------------
    NATIVE_CALL   = auto()  # dest, native_name, arg_temps(list)
    IMPORT_MODULE = auto()  # dest_module, name_temp/str
    IMPORT_SYMBOL = auto()  # dest, module_temp, name_temp/str

    # ---------------------------------
    # Debug / System
    # ---------------------------------
    NOP         = auto()    # -
    DEBUG_PRINT = auto()    # value_temp
    HALT        = auto()    # -


class IRInstruction:
    """
    Eine einzelne IR-Instruktion:
      - op: OpCode
      - args: Liste von Operanden (Temps, Variablennamen, Labelnamen, Literale)

    Beispiel:
      IRInstruction(OpCode.LOAD_CONST, "%t0", 42)
      IRInstruction(OpCode.JUMP_IF_FALSE, "%t1", "Lend")
    """

    __slots__ = ("op", "args")

    def __init__(self, op: OpCode, *args):
        self.op = op
        self.args = list(args)

    def __repr__(self) -> str:
        if self.args:
            args_repr = ", ".join(repr(a) for a in self.args)
            return f"IR({self.op.name}, {args_repr})"
        return f"IR({self.op.name})"


class IRLabel:
    """
    Label als separate Entität in der Instruktionsliste.
    Der IRBuilder kann daraus Sprungziele auflösen oder
    der Codegen kann Labels direkt in Blöcke/GOTO übersetzen.
    """

    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"LABEL({self.name})"
