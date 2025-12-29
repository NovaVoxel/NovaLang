# ============================================
# Nova package builder with LTO support
# Compiles nova/ → bin/*.nomc and packs into target/<project>.novar
# ============================================

import os
import tarfile
import json

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.ir_builder import build_ir
from compiler.codegen_nomc import generate_nomc
from compiler.issues import IssueReporter


def build_novar(project_name, source_dir="nova", bin_dir="bin", target_dir="target"):
    # Ensure directories exist
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)

    reporter = IssueReporter()
    compiled_files = []

    # ----------------------------------------
    # Collect .nova files
    # ----------------------------------------
    if not os.path.isdir(source_dir):
        reporter.error(f"Source directory not found: {source_dir}")
        reporter.report()
        return None

    nova_files = sorted(
        f for f in os.listdir(source_dir)
        if f.endswith(".nova")
    )

    if not nova_files:
        reporter.warning("No .nova files found to compile")
        reporter.report()

    # ----------------------------------------
    # Compile each .nova file
    # ----------------------------------------
    for fname in nova_files:
        path = os.path.join(source_dir, fname)

        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            reporter.error(f"Failed to read {fname}: {e}")
            continue

        # Tokenize + parse
        try:
            tokens = list(tokenize(code))
            ast = parse(tokens, reporter=reporter)
        except Exception as e:
            reporter.error(f"Failed to parse {fname}: {e}")
            continue

        if reporter.has_errors():
            reporter.report()
            return None

        # Build IR
        try:
            ir_module = build_ir(ast)
        except Exception as e:
            reporter.error(f"IR generation failed for {fname}: {e}")
            continue

        # Output .nomc file
        nomc_path = os.path.join(bin_dir, fname.replace(".nova", ".nomc"))

        try:
            generate_nomc(ir_module, output=nomc_path)
            compiled_files.append(nomc_path)
        except Exception as e:
            reporter.error(f"Codegen failed for {fname}: {e}")
            continue

    # ----------------------------------------
    # Write manifest
    # ----------------------------------------
    manifest = {
        "project": {
            "name": project_name,
            "version": "0.1.0"
        },
        "bin": compiled_files
    }

    manifest_path = os.path.join(bin_dir, "Manifest.json")
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    except Exception as e:
        reporter.error(f"Failed to write manifest: {e}")
        reporter.report()
        return None

    # ----------------------------------------
    # Pack .novar archive
    # ----------------------------------------
    novar_path = os.path.join(target_dir, f"{project_name}.novar")

    try:
        with tarfile.open(novar_path, "w") as tar:
            tar.add(bin_dir, arcname="bin")
    except Exception as e:
        reporter.error(f"Failed to create .novar archive: {e}")
        reporter.report()
        return None

    print(f"✅ Built {novar_path} with LTO")
    return novar_path
