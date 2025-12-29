# Nova launcher
# Loads .novar, extracts .nomc, and executes native machine code

import json, tarfile, os, subprocess

def launch(novar_path):
    # Extract novar
    with tarfile.open(novar_path, "r") as tar:
        tar.extractall("target_extracted")

    # Load manifest
    manifest_path = os.path.join("target_extracted", "bin", "Manifest.json")
    with open(manifest_path) as f:
        manifest = json.load(f)

    print(f"Launching {manifest['project']['name']} v{manifest['project']['version']}")

    # Execute each .nomc file (native machine code)
    for nomc_file in manifest["bin"]:
        path = os.path.join("target_extracted", nomc_file)
        subprocess.run([path])  # run native binary directly
