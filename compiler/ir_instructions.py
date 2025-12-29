# ============================================
# Nova IR Instruction Set
# Defines all supported opcodes for lowering to LLVM
# ============================================

INSTRUCTIONS = {
    # ========================================
    # Arithmetic (SSA: dst = op a b)
    # ========================================
    "ADD":  {"args": ["dst", "a", "b"], "pure": True},
    "SUB":  {"args": ["dst", "a", "b"], "pure": True},
    "MUL":  {"args": ["dst", "a", "b"], "pure": True},
    "DIV":  {"args": ["dst", "a", "b"], "pure": True},
    "MOD":  {"args": ["dst", "a", "b"], "pure": True},

    # ========================================
    # Constants & variables
    # ========================================
    "LOAD_CONST": {"args": ["dst", "value"], "pure": True},
    "LOAD_VAR":   {"args": ["dst", "name"],  "pure": False},
    "STORE_VAR":  {"args": ["name", "src"],  "pure": False},

    # ========================================
    # Control flow
    # ========================================
    "JUMP":          {"args": ["label"], "terminator": True},
    "JUMP_IF_FALSE": {"args": ["cond", "label"], "terminator": True},
    "RETURN":        {"args": ["value?"], "terminator": True},

    # LABEL is NOT an instruction — it's a block header
    # Blocks are represented by IRBlock objects

    # ========================================
    # Function calls
    # ========================================
    # SSA: dst = CALL func, [args...]
    "CALL": {"args": ["dst", "func", "args*"], "pure": False},

    # ========================================
    # Builtins (all SSA)
    # ========================================
    "PRINT_CONST": {"args": ["value"], "pure": False},
    "PRINT":       {"args": ["value"], "pure": False},

    "LEN": {"args": ["dst", "seq"], "pure": True},
    "SUM": {"args": ["dst", "seq"], "pure": True},
    "MIN": {"args": ["dst", "seq"], "pure": True},
    "MAX": {"args": ["dst", "seq"], "pure": True},
}
