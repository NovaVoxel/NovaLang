from .parser import FunctionDef, UseStmt

def transpile(ast):
    py_lines = [
        "from runtime.native import __native__"  # Hook for Nova-Stdlib
    ]
    for node in ast:
        if isinstance(node, UseStmt):
            # Nova: use modulename → Python: import modulename
            py_lines.append(f"import {node.module}")
        elif isinstance(node, FunctionDef):
            py_lines.append(f"def {node.name}():")
            py_lines.append("    # Hier könnte AST → Python Body transpiliert werden")
            py_lines.append("    pass")
    return "\n".join(py_lines)
