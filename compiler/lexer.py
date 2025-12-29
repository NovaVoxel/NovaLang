import re
from dataclasses import dataclass

# ============================
# Token definition
# ============================

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.column})"


# ============================
# Token specifications
# ============================

KEYWORDS = {
    "def", "let", "use", "return", "funk", "if", "else", "while", "for", "in"
}

TOKEN_REGEX = [
    ("NUMBER",   r"\d+"),
    ("STRING",   r'"[^"\n]*"|\'[^\'\n]*\''),
    ("IDENT",    r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",       r"==|!=|<=|>=|\+|\-|\*|\/|=|<|>"),
    ("LPAREN",   r"`\("),
    ("RPAREN",   r"\)`"),
    ("LBRACE",   r"\{"),
    ("RBRACE",   r"\}"),
    ("LBRACK",   r"\["),
    ("RBRACK",   r"\]"),
    ("COLON",    r":"),
    ("COMMA",    r","),
]

MASTER_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_REGEX)
)


# ============================
# Lexer class
# ============================

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.indent_stack = [0]

    def error(self, msg):
        raise SyntaxError(f"[Line {self.line}, Col {self.col}] {msg}")

    def peek(self):
        return self.code[self.pos] if self.pos < len(self.code) else ""

    def advance(self, n=1):
        for _ in range(n):
            if self.pos < len(self.code):
                if self.code[self.pos] == "\n":
                    self.line += 1
                    self.col = 1
                else:
                    self.col += 1
                self.pos += 1

    def skip_whitespace(self):
        while self.peek() in " \t":
            self.advance()

    def skip_comment(self):
        if self.peek() == "#":
            while self.peek() not in ("\n", ""):
                self.advance()

    def handle_indentation(self):
        start = self.pos
        while self.peek() == " ":
            self.advance()

        indent = self.pos - start

        if self.peek() == "\n" or self.peek() == "":
            return []  # empty line → ignore indentation

        tokens = []

        if indent > self.indent_stack[-1]:
            self.indent_stack.append(indent)
            tokens.append(Token("INDENT", indent, self.line, self.col))
        else:
            while indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                tokens.append(Token("DEDENT", indent, self.line, self.col))

            if indent != self.indent_stack[-1]:
                self.error("Invalid indentation level")

        return tokens

    def tokenize(self):
        tokens = []

        while self.pos < len(self.code):
            ch = self.peek()

            # Newline
            if ch == "\n":
                tokens.append(Token("NEWLINE", "\n", self.line, self.col))
                self.advance()
                tokens.extend(self.handle_indentation())
                continue

            # Comments
            if ch == "#":
                self.skip_comment()
                continue

            # Whitespace
            if ch in " \t":
                self.skip_whitespace()
                continue

            # Try matching tokens
            match = MASTER_REGEX.match(self.code, self.pos)
            if match:
                token_type = match.lastgroup
                value = match.group(token_type)
                token = Token(token_type, value, self.line, self.col)

                # Keyword check
                if token_type == "IDENT" and value in KEYWORDS:
                    token.type = value.upper()

                tokens.append(token)
                self.advance(len(value))
                continue

            # Unknown character
            self.error(f"Unexpected character: {ch!r}")

        # Close all indentation levels
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            tokens.append(Token("DEDENT", "", self.line, self.col))

        tokens.append(Token("EOF", "", self.line, self.col))
        return tokens


# ============================
# Example usage
# ============================

if __name__ == "__main__":
    code = """
def test(x):
    let y = 10
    funk {
        return y + x
    }
"""

    lexer = Lexer(code)
    for tok in lexer.tokenize():
        print(tok)
