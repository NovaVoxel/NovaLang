import os
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.transpiler import transpile
from compiler.packager import package

SOURCE_DIR = "nova"
BIN_DIR = "bin"
ENTRY_FILE = "main.nova"

def build():
    with open(os.path.join(SOURCE_DIR, ENTRY_FILE)) as f:
        code = f.read()

    tokens = list(tokenize(code))
    ast = parse(tokens)
    py_code = transpile(ast)

    os.makedirs(BIN_DIR, exist_ok=True)
    py_path = os.path.join(BIN_DIR, "main.py")
    with open(py_path, "w") as f:
        f.write(py_code)

    package("Nova Project", "main.py", BIN_DIR)

    print("✅ Build abgeschlossen")

if __name__ == "__main__":
    build()
