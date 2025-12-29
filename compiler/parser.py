# compiler/parser.py

from compiler.lexer import TokenType
from compiler.ast import (
    BlockNode,
    WhileNode,
    ForEachNode,
    VarAssignNode,
    VarRefNode,
    CallNode,
    NumberNode,
    StringNode,
    BinaryOpNode,
)


class Parser:
    def __init__(self, tokens, reporter=None):
        self.tokens = tokens
        self.pos = 0
        self.reporter = reporter

    def current(self):
        return self.tokens[self.pos]

    def match(self, type_):
        if self.current().type == type_:
            tok = self.current()
            self.pos += 1
            return tok
        return None

    def expect(self, type_):
        tok = self.current()
        if tok.type != type_:
            raise SyntaxError(f"Expected {type_}, got {tok.type} at {tok.line}:{tok.column}")
        self.pos += 1
        return tok

    def check(self, type_):
        return self.current().type == type_

    # Entry ---------------------------------------------------

    def parse(self):
        stmts = []
        while self.current().type != TokenType.EOF:
            stmts.append(self.parse_statement())
        return BlockNode(stmts)

    # Statements ----------------------------------------------

    def parse_statement(self):
        tok = self.current()

        if tok.type == TokenType.FOR:
            return self.parse_for_each()

        if tok.type == TokenType.WHILE:
            return self.parse_while()
        if tok.type == TokenType.IDENT:
            # lookahead for assignment
            if self.tokens[self.pos + 1].type == TokenType.EQUAL:
                return self.parse_assignment()
            else:
                expr = self.parse_expression()
                self.match(TokenType.SEMICOLON)
                return expr

        # Block
        if tok.type == TokenType.LBRACE:
            return self.parse_block()

        # Fallback: Expression-Statement
        expr = self.parse_expression()
        self.match(TokenType.SEMICOLON)
        return expr

    def parse_block(self):
        lbrace = self.expect(TokenType.LBRACE)
        stmts = []
        while not self.check(TokenType.RBRACE):
            stmts.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return BlockNode(stmts, span=(lbrace.line, lbrace.column))

    def parse_while(self):
        while_tok = self.expect(TokenType.WHILE)
        cond = self.parse_expression()
        body = self.parse_block()
        return WhileNode(cond, body, span=(while_tok.line, while_tok.column))

    def parse_for_each(self):
        for_tok = self.expect(TokenType.FOR)

        vars_ = [self.expect(TokenType.IDENT).value]
        if self.match(TokenType.COMMA):
            vars_.append(self.expect(TokenType.IDENT).value)

        iterable = self.parse_expression()
        body = self.parse_block()

        return ForEachNode(vars_, iterable, body, span=(for_tok.line, for_tok.column))

    def parse_assignment(self):
        name_tok = self.expect(TokenType.IDENT)
        self.expect(TokenType.EQUAL)
        expr = self.parse_expression()
        self.match(TokenType.SEMICOLON)
        return VarAssignNode(name_tok.value, expr, span=(name_tok.line, name_tok.column))

    # Expressions ---------------------------------------------

    def parse_expression(self):
        return self.parse_add()

    def parse_add(self):
        node = self.parse_term()
        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            op = self.current().type
            self.pos += 1
            right = self.parse_term()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.check(TokenType.STAR) or self.check(TokenType.SLASH):
            op = self.current().type
            self.pos += 1
            right = self.parse_factor()
            node = BinaryOpNode(node, op, right)
        return node

    def parse_factor(self):
        tok = self.current()

        if tok.type == TokenType.NUMBER:
            self.pos += 1
            return NumberNode(tok.value)

        if tok.type == TokenType.STRING:
            self.pos += 1
            return StringNode(tok.value)

        if tok.type == TokenType.IDENT:
            if self.tokens[self.pos + 1].type == TokenType.LPAREN:
                return self.parse_call()
            self.pos += 1
            return VarRefNode(tok.value)

        if tok.type == TokenType.LPAREN:
            self.pos += 1
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"Unexpected token {tok.type} at {tok.line}:{tok.column}")

    def parse_call(self):
        ident = self.expect(TokenType.IDENT)
        self.expect(TokenType.LPAREN)
        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expression())
        self.expect(TokenType.RPAREN)
        return CallNode(VarRefNode(ident.value), args)
