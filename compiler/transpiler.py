from .parser import FunctionDef, UseStmt

def transpile(ast):
    py_lines = []
    for node in ast:
        if isinstance(node, UseStmt):
            py_lines.append(f"import {node.module}")
        elif isinstance(node, FunctionDef):
            py_lines.append(f"def {node.name}():")
            py_lines.append("    print('Nova function executed')")
    return "\n".join(py_lines)
