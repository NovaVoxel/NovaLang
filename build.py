import os
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.ir_builder import build_ir
from compiler.codegen_nomc import generate_nomc
from compiler.packager import package

SOURCE_DIR = "nova"
BIN_DIR = "bin"
ENTRY_FILE = "main.nova"

def build():
    with open(os.path.join(SOURCE_DIR, ENTRY_FILE)) as f:
        code = f.read()

    tokens = list(tokenize(code))
    ast = parse(tokens)
    ir_module = build_ir(ast)
    obj_path = generate_nomc(ir_module, output=os.path.join(BIN_DIR, "main.o"))

    package("Nova Project", "main.o", BIN_DIR)

    print("✅ Build finished")
    print(f"→ {obj_path}")
    print("→ Manifest.json created")

if __name__ == "__main__":
    build()
