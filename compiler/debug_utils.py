# ============================================
# Nova Debug Utilities
# Provides syntax checking and AST/IR inspection
# ============================================

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.ir_builder import build_ir
from compiler.issues import IssueReporter


# --------------------------------------------
# Syntax checking
# --------------------------------------------

def check_syntax(source_code: str, *, dump_tokens=False, dump_ast=False):
    reporter = IssueReporter()

    try:
        # Tokenize
        tokens = list(tokenize(source_code))

        if dump_tokens:
            print("=== Token Dump ===")
            for t in tokens:
                print(t)
            print()

        # Parse
        ast = parse(tokens, reporter=reporter)

        if reporter.has_errors():
            reporter.report()
            return None

        if dump_ast:
            dump_ast_tree(ast)

        return ast

    except Exception as e:
        reporter.error(f"Internal compiler error: {e}")
        reporter.report()
        return None


# --------------------------------------------
# AST Dump
# --------------------------------------------

def dump_ast_tree(ast):
    if not ast:
        print("=== AST Dump === (empty)")
        return

    print("=== AST Dump ===")
    for node in ast:
        print(node)
    print()


# --------------------------------------------
# IR Dump
# --------------------------------------------

def dump_ir(ast):
    if not ast:
        print("=== IR Dump === (no AST)")
        return

    try:
        ir_module = build_ir(ast)
        print("=== IR Dump ===")
        print(ir_module)
        print()
    except Exception as e:
        print("=== IR Generation Failed ===")
        print(e)
