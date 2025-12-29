class FunctionDef:
    """
    AST node representing a function definition in Nova.

    Example:
        def add(x, y):
            return x + y
    """

    def __init__(self, name, params=None, body=None, return_type=None, location=None):
        self.name = name
        self.params = params or []      # list of parameter names
        self.body = body                # Block node
        self.return_type = return_type  # optional type annotation
        self.location = location        # (line, column) for error reporting

    def __repr__(self):
        return (
            f"FunctionDef(name={self.name!r}, "
            f"params={self.params}, "
            f"return_type={self.return_type}, "
            f"body={self.body})"
        )
