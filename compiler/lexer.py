import re

TOKENS = [
    ("DEF", r"def"),
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("NUMBER", r"\d+"),
    ("LPAREN", r"`\("),
    ("RPAREN", r"\)`"),
    ("COLON", r":"),
    ("NEWLINE", r"\n"),
    ("INDENT", r"[ ]+"),
]

def tokenize(code: str):
    pos = 0
    while pos < len(code):
        match = None
        for token_type, pattern in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                yield (token_type, match.group(0))
                pos = match.end(0)
                break
        if not match:
            pos += 1
