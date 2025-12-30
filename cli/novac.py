# novac.py — Nova Compiler Entry Point

import sys
import os

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.ir_builder import build_ir
from compiler.codegen_nomc import generate_nomc
from compiler.issues import IssueReporter

from novar_builder import build_novar  


def compile_nomc(path: str):
    """Compile a single .nova file into a .nomc file."""
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)

    reporter = IssueReporter()

    # Read source
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        sys.exit(1)

    # Tokenize + parse
    try:
        tokens = list(tokenize(code))
        ast = parse(tokens, reporter=reporter)
    except Exception as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    if reporter.has_errors():
        reporter.report()
        sys.exit(1)

    # IR
    try:
        ir_module = build_ir(ast)
    except Exception as e:
        print(f"IR generation failed: {e}")
        sys.exit(1)

    # Output path (.nova → .nomc)
    if path.endswith(".nova"):
        out_path = path[:-5] + ".nomc"
    else:
        out_path = path + ".nomc"

    # Codegen
    try:
        generate_nomc(ir_module, output=out_path)
    except Exception as e:
        print(f"Codegen failed: {e}")
        sys.exit(1)

    print(f"✅ Compiled .nova → .nomc: {out_path}")


def compile_project(project_root: str):
    """Compile a full Nova project into a .novar archive."""
    if not os.path.isdir(project_root):
        print(f"Error: Project root not found: {project_root}")
        sys.exit(1)

    # z.B.:
    # project_root/
    #   nova/    -> .nova Sources
    #   bin/     -> .nomc Output
    #   target/  -> .novar Output
    project_name = os.path.basename(os.path.abspath(project_root))
    source_dir = os.path.join(project_root, "nova")
    bin_dir = os.path.join(project_root, "bin")
    target_dir = os.path.join(project_root, "target")

    novar_path = build_novar(
        project_name=project_name,
        source_dir=source_dir,
        bin_dir=bin_dir,
        target_dir=target_dir,
    )

    if novar_path is None:
        print("Build failed.")
        sys.exit(1)

    print(f"✅ Compiled project → {novar_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  novac -n <file.nova>")
        print("  novac -p <project root>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "-n":
        compile_nomc(sys.argv[2])
    elif mode == "-p":
        compile_project(sys.argv[2])
    else:
        print(f"Unknown option: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
