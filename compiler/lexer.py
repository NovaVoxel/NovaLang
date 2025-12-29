# compiler/lexer.py

from enum import Enum, auto

class TokenType(Enum):
    # Single char
    LBRACE = auto()
    RBRACE = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    SEMICOLON = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQUAL = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()       
    FUNC = auto()
    RETURN = auto()

    # Literals / Identifiers
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()

    EOF = auto()


KEYWORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
}


class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    def __init__(self, src: str):
        self.src = src
        self.pos = 0
        self.line = 1
        self.col = 1

    def current_char(self):
        if self.pos >= len(self.src):
            return None
        return self.src[self.pos]

    def advance(self):
        ch = self.current_char()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1

    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char().isspace():
            self.advance()

    def identifier(self):
        start_col = self.col
        start_pos = self.pos
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == "_"):
            self.advance()
        text = self.src[start_pos:self.pos]
        type_ = KEYWORDS.get(text, TokenType.IDENT)
        return Token(type_, text, self.line, start_col)

    def number(self):
        start_col = self.col
        start_pos = self.pos
        while self.current_char() is not None and self.current_char().isdigit():
            self.advance()
        text = self.src[start_pos:self.pos]
        return Token(TokenType.NUMBER, int(text), self.line, start_col)

    def string(self):
        start_col = self.col
        quote = self.current_char()
        self.advance()  # skip quote
        start_pos = self.pos
        while self.current_char() is not None and self.current_char() != quote:
            self.advance()
        text = self.src[start_pos:self.pos]
        self.advance()  # closing quote
        return Token(TokenType.STRING, text, self.line, start_col)

    def next_token(self):
        self.skip_whitespace()
        ch = self.current_char()
        if ch is None:
            return Token(TokenType.EOF, "", self.line, self.col)

        if ch.isalpha() or ch == "_":
            return self.identifier()

        if ch.isdigit():
            return self.number()

        if ch in ("'", '"'):
            return self.string()

        line, col = self.line, self.col

        if ch == "{":
            self.advance()
            return Token(TokenType.LBRACE, "{", line, col)
        if ch == "}":
            self.advance()
            return Token(TokenType.RBRACE, "}", line, col)
        if ch == "(":
            self.advance()
            return Token(TokenType.LPAREN, "(", line, col)
        if ch == ")":
            self.advance()
            return Token(TokenType.RPAREN, ")", line, col)
        if ch == ",":
            self.advance()
            return Token(TokenType.COMMA, ",", line, col)
        if ch == ";":
            self.advance()
            return Token(TokenType.SEMICOLON, ";", line, col)
        if ch == "+":
            self.advance()
            return Token(TokenType.PLUS, "+", line, col)
        if ch == "-":
            self.advance()
            return Token(TokenType.MINUS, "-", line, col)
        if ch == "*":
            self.advance()
            return Token(TokenType.STAR, "*", line, col)
        if ch == "/":
            self.advance()
            return Token(TokenType.SLASH, "/", line, col)
        if ch == "=":
            self.advance()
            return Token(TokenType.EQUAL, "=", line, col)

        raise SyntaxError(f"Unexpected char {ch!r} at {line}:{col}")

    def tokenize(self):
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens
