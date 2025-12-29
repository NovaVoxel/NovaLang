# Nova Debug Utilities
# Provides syntax checking and AST/IR inspection

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.ir_builder import build_ir
from compiler.issues import IssueReporter

def check_syntax(source_code: str):
    reporter = IssueReporter()
    try:
        tokens = list(tokenize(source_code))
        ast = parse(tokens, reporter=reporter)
        if reporter.has_errors():
            reporter.report()
            return None
        return ast
    except Exception as e:
        reporter.error(str(e))
        reporter.report()
        return None

def dump_ast(ast):
    if ast:
        print("=== AST Dump ===")
        for node in ast:
            print(node)

def dump_ir(ast):
    if ast:
        ir_module = build_ir(ast)
        print("=== IR Dump ===")
        print(ir_module)
