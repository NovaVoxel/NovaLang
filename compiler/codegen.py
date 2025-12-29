def generate(ast):
    output = []
    for node in ast:
        if isinstance(node, FunctionDef):
            output.append(f"FUNC {node.name}")
    return "\n".join(output)
