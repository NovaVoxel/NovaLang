# Nova package builder
# Compiles nova/ → bin/*.nomc and packs into target/<project>.novar

import os, tarfile, json
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.ir_builder import build_ir
from compiler.codegen_nomc import generate_nomc

def build_novar(project_name, source_dir="nova", bin_dir="bin", target_dir="target"):
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)

    compiled_files = []
    for fname in os.listdir(source_dir):
        if fname.endswith(".nova"):
            path = os.path.join(source_dir, fname)
            with open(path) as f:
                code = f.read()
            tokens = list(tokenize(code))
            ast = parse(tokens)
            ir_module = build_ir(ast)
            nomc_path = os.path.join(bin_dir, fname.replace(".nova", ".nomc"))
            generate_nomc(ir_module, output=nomc_path)
            compiled_files.append(nomc_path)

    manifest = {
        "project": {"name": project_name, "version": "0.1.0"},
        "bin": compiled_files
    }
    manifest_path = os.path.join(bin_dir, "Manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    novar_path = os.path.join(target_dir, f"{project_name}.novar")
    with tarfile.open(novar_path, "w") as tar:
        tar.add(bin_dir, arcname="bin")

    print(f"✅ Built {novar_path}")
    return novar_path
