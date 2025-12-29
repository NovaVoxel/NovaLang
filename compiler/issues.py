# Nova Issue Reporter
# Collects and formats compiler errors/warnings for clear output

class Issue:
    def __init__(self, kind, message, line=None, col=None):
        self.kind = kind      # "error" or "warning"
        self.message = message
        self.line = line
        self.col = col

    def __repr__(self):
        pos = f"(line {self.line}, col {self.col})" if self.line is not None else ""
        return f"[{self.kind.upper()}] {self.message} {pos}"

class IssueReporter:
    def __init__(self):
        self.issues = []

    def error(self, message, line=None, col=None):
        self.issues.append(Issue("error", message, line, col))

    def warning(self, message, line=None, col=None):
        self.issues.append(Issue("warning", message, line, col))

    def has_errors(self):
        return any(i.kind == "error" for i in self.issues)

    def has_warnings(self):
        return any(i.kind == "warning" for i in self.issues)

    def report(self):
        if not self.issues:
            return  # ✅ nothing printed if all is fine
        print("=== Issues ===")
        for issue in self.issues:
            print(issue)
