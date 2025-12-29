# Nova Build Script
# Compiles nova/*.nova → bin/*.nomc → target/<project>.novar
# Uses IssueReporter for syntax checking, aborts build if errors exist

import os
import sys
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.ir_builder import build_ir
from compiler.codegen_nomc import generate_nomc
from compiler.novar_builder import build_novar
from compiler.issues import IssueReporter

SOURCE_DIR = "nova"
BIN_DIR = "bin"
TARGET_DIR = "target"
PROJECT_NAME = "NovaProject"
ENTRY_FILE = "main.nova"

def build():
    os.makedirs(BIN_DIR, exist_ok=True)
    os.makedirs(TARGET_DIR, exist_ok=True)

    reporter = IssueReporter()

    # Compile all .nova files in source_dir
    compiled_files = []
    for fname in os.listdir(SOURCE_DIR):
        if fname.endswith(".nova"):
            path = os.path.join(SOURCE_DIR, fname)
            with open(path) as f:
                code = f.read()

            # Syntax check
            try:
                tokens = list(tokenize(code))
                ast = parse(tokens, reporter=reporter)
            except Exception as e:
                reporter.error(str(e))
                reporter.report()
                sys.exit(1)

            if reporter.has_errors():
                reporter.report()
                sys.exit(1)

            # Build IR and compile to .nomc
            ir_module = build_ir(ast)
            nomc_path = os.path.join(BIN_DIR, fname.replace(".nova", ".nomc"))
            generate_nomc(ir_module, output=nomc_path)
            compiled_files.append(nomc_path)

    # Package into NovAr
    novar_path = build_novar(PROJECT_NAME, source_dir=SOURCE_DIR,
                             bin_dir=BIN_DIR, target_dir=TARGET_DIR)

    # Only print success if no issues
    if not reporter.has_errors() and not reporter.has_warnings():
        print(f"✅ Build finished: {novar_path}")

if __name__ == "__main__":
    build()
