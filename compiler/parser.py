# ============================
# AST Nodes
# ============================

class FunctionDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FunctionDef(name={self.name}, params={self.params}, body={self.body})"


class UseStmt:
    def __init__(self, module):
        self.module = module

    def __repr__(self):
        return f"UseStmt(module={self.module})"


class Block:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"


# ============================
# Parser
# ============================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    # Utility helpers
    def peek(self, offset=0):
        if self.i + offset < len(self.tokens):
            return self.tokens[self.i + offset]
        return None

    def advance(self):
        tok = self.peek()
        self.i += 1
        return tok

    def expect(self, type_):
        tok = self.peek()
        if not tok or tok.type != type_:
            raise SyntaxError(f"Expected {type_}, got {tok}")
        return self.advance()

    # ============================
    # Top-level parse
    # ============================

    def parse(self):
        ast = []

        while self.peek() and self.peek().type != "EOF":
            tok = self.peek()

            if tok.type == "USE":
                ast.append(self.parse_use())

            elif tok.type == "DEF":
                ast.append(self.parse_function())

            else:
                self.advance()  # skip unknown

        return ast

    # ============================
    # use <module>
    # ============================

    def parse_use(self):
        self.expect("USE")
        ident = self.expect("IDENT")
        return UseStmt(ident.value)

    # ============================
    # def <name>(params): NEWLINE INDENT block DEDENT
    # ============================

    def parse_function(self):
        self.expect("DEF")
        name = self.expect("IDENT").value

        self.expect("LPAREN")
        params = self.parse_params()
        self.expect("RPAREN")

        self.expect("COLON")
        self.expect("NEWLINE")

        body = self.parse_block()

        return FunctionDef(name, params, body)

    # ============================
    # Parameter list
    # ============================

    def parse_params(self):
        params = []

        if self.peek().type == "RPAREN":
            return params

        while True:
            ident = self.expect("IDENT")
            params.append(ident.value)

            if self.peek().type == "COMMA":
                self.advance()
                continue
            break

        return params

    # ============================
    # Block: INDENT ... DEDENT
    # ============================

    def parse_block(self):
        statements = []

        self.expect("INDENT")

        while True:
            tok = self.peek()

            if tok.type == "DEDENT":
                self.advance()
                break

            if tok.type == "USE":
                statements.append(self.parse_use())

            elif tok.type == "DEF":
                statements.append(self.parse_function())

            else:
                self.advance()  # skip unknown

        return Block(statements)


# ============================
# Example usage
# ============================

if __name__ == "__main__":
    from lexer import Lexer  

    code = """
use math

def test(x, y):
    use io
    def inner(z):
        use sys
"""

    tokens = Lexer(code).tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    for node in ast:
        print(node)
