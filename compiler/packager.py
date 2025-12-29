import json
import os

def package(project_name, entry_file, bin_dir="bin"):
    manifest = {
        "project": {"name": project_name, "version": "0.1.0"},
        "entry": f"{bin_dir}/{entry_file}"
    }
    os.makedirs(bin_dir, exist_ok=True)
    with open("Manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
