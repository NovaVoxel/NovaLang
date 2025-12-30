# compiler/ast.py


class BlockNode:
    def __init__(self, statements, span=None):
        self.statements = statements
        self.span = span


class WhileNode:
    def __init__(self, condition, body, span=None):
        self.condition = condition
        self.body = body
        self.span = span


class ForEachNode:
    """
    for i expr { ... }
    for k,v expr { ... }
    vars: ["i"] oder ["k","v"]
    iterable: ExpressionNode
    body: BlockNode
    """
    def __init__(self, vars_, iterable, body, span=None):
        self.vars = vars_
        self.iterable = iterable
        self.body = body
        self.span = span


class VarAssignNode:
    def __init__(self, name, expr, span=None):
        self.name = name
        self.expr = expr
        self.span = span


class VarRefNode:
    def __init__(self, name, span=None):
        self.name = name
        self.span = span


class CallNode:
    def __init__(self, func, args, span=None):
        self.func = func
        self.args = args
        self.span = span


class NumberNode:
    def __init__(self, value, span=None):
        self.value = value
        self.span = span


class StringNode:
    def __init__(self, value, span=None):
        self.value = value
        self.span = span


class BinaryOpNode:
    def __init__(self, left, op, right, span=None):
        self.left = left
        self.op = op
        self.right = right
        self.span = span
