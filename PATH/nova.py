# nova.py — Nova Runtime Loader

import sys
import os
import tarfile
import json

from loader import load_nomc, load_novar
from vm import NovaVM


def run_nomc(path: str):
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)

    bytecode = load_nomc(path)
    vm = NovaVM()
    vm.run(bytecode)


def run_novar(path: str):
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)

    # Extract .novar
    extract_dir = path + "_extracted"
    os.makedirs(extract_dir, exist_ok=True)

    with tarfile.open(path, "r") as tar:
        tar.extractall(extract_dir)

    # Load manifest
    manifest_path = os.path.join(extract_dir, "bin", "Manifest.json")
    if not os.path.exists(manifest_path):
        print("Error: Manifest.json missing in .novar")
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    vm = NovaVM()

    # Execute all .nomc files in order
    for nomc_path in manifest["bin"]:
        full_path = os.path.join(extract_dir, nomc_path)
        bytecode = load_nomc(full_path)
        vm.run(bytecode)


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  nova -nomc <file.nomc>")
        print("  nova -novar <file.novar>")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "-nomc":
        run_nomc(sys.argv[2])
    elif mode == "-novar":
        run_novar(sys.argv[2])
    else:
        print(f"Unknown option: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
