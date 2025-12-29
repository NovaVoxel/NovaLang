# Nova IR Instruction Set
# Defines all supported opcodes for lowering to LLVM

INSTRUCTIONS = {
    # Arithmetic
    "ADD": {"args": 3},   # dst, a, b
    "SUB": {"args": 3},
    "MUL": {"args": 3},
    "DIV": {"args": 3},
    "MOD": {"args": 3},

    # Constants & variables
    "LOAD_CONST": {"args": 2},  # dst, value
    "LOAD_VAR": {"args": 2},    # dst, name
    "STORE_VAR": {"args": 2},   # name, src

    # Control flow
    "JUMP": {"args": 1},        # label
    "JUMP_IF_FALSE": {"args": 2}, # cond, label
    "LABEL": {"args": 1},

    # Functions
    "CALL": {"args": 2},        # func, argc
    "RETURN": {"args": 0},

    # Builtins
    "PRINT_CONST": {"args": 1}, # string literal
    "PRINT": {"args": 1},       # slot
    "LEN": {"args": 2},         # dst, seq
    "SUM": {"args": 2},         # dst, seq
    "MIN": {"args": 2},
    "MAX": {"args": 2},
}
