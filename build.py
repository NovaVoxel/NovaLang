import os
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.codegen import generate
from compiler.packager import package

SOURCE_DIR = "nova"
BIN_DIR = "bin"
ENTRY_FILE = "main.nova"

def build():
    # 1. Source laden
    with open(os.path.join(SOURCE_DIR, ENTRY_FILE)) as f:
        code = f.read()

    # 2. Lexer
    tokens = list(tokenize(code))

    # 3. Parser
    ast = parse(tokens)

    # 4. Codegen → NOMC
    nomc_code = generate(ast)
    os.makedirs(BIN_DIR, exist_ok=True)
    nomc_path = os.path.join(BIN_DIR, "main.nomc")
    with open(nomc_path, "w") as f:
        f.write(nomc_code)

    # 5. Packager → Manifest.json
    package("Nova Project", "main.nomc", BIN_DIR)

    print("✅ Build abgeschlossen")
    print(f"→ {nomc_path}")
    print("→ Manifest.json erstellt")

if __name__ == "__main__":
    build()
