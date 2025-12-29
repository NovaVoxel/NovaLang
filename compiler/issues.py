# ============================================
# Nova Issue Reporter
# Collects, formats and manages compiler issues
# ============================================

import sys
from dataclasses import dataclass
from typing import Optional, List


# --------------------------------------------
# Single issue
# --------------------------------------------

@dataclass
class Issue:
    kind: str               # "error" or "warning"
    message: str
    line: Optional[int] = None
    col: Optional[int] = None
    code: Optional[str] = None   # e.g. NOVA001

    def __repr__(self):
        loc = ""
        if self.line is not None:
            loc = f"(line {self.line}, col {self.col})"

        code = f"[{self.code}] " if self.code else ""
        return f"[{self.kind.upper()}] {code}{self.message} {loc}".rstrip()


# --------------------------------------------
# Issue Reporter
# --------------------------------------------

class IssueReporter:
    def __init__(self):
        self.issues: List[Issue] = []

    # --------------------------
    # Add issues
    # --------------------------

    def error(self, message, line=None, col=None, code=None):
        self.issues.append(Issue("error", message, line, col, code))

    def warning(self, message, line=None, col=None, code=None):
        self.issues.append(Issue("warning", message, line, col, code))

    # --------------------------
    # Query
    # --------------------------

    def has_errors(self):
        return any(i.kind == "error" for i in self.issues)

    def has_warnings(self):
        return any(i.kind == "warning" for i in self.issues)

    def count_errors(self):
        return sum(1 for i in self.issues if i.kind == "error")

    def count_warnings(self):
        return sum(1 for i in self.issues if i.kind == "warning")

    # --------------------------
    # Output formatting
    # --------------------------

    def report(self, stream=sys.stdout):
        if not self.issues:
            return

        # Sort: errors first, then warnings, then by line
        self.issues.sort(
            key=lambda i: (0 if i.kind == "error" else 1, i.line or -1)
        )

        print("=== Nova Compiler Issues ===", file=stream)

        for issue in self.issues:
            print(issue, file=stream)

        print(
            f"\n{self.count_errors()} error(s), {self.count_warnings()} warning(s)",
            file=stream
        )

    # --------------------------
    # Clear issues (for multi-pass compilers)
    # --------------------------

    def reset(self):
        self.issues.clear()
