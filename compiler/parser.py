class FunctionDef:
    def __init__(self, name, body):
        self.name = name
        self.body = body

class UseStmt:
    def __init__(self, module):
        self.module = module

def parse(tokens):
    ast = []
    tokens = list(tokens)
    i = 0
    while i < len(tokens):
        if tokens[i][0] == "DEF":
            name = tokens[i+1][1]
            ast.append(FunctionDef(name, []))
            i += 2
        elif tokens[i][0] == "USE":
            module = tokens[i+1][1]
            ast.append(UseStmt(module))
            i += 2
        else:
            i += 1
    return ast
