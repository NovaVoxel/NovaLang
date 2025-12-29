import json
import runpy
from .native import __native__

def launch():
    with open("Manifest.json") as f:
        manifest = json.load(f)
    entry = manifest["entry"]

    print(f"Launching {manifest['project']['name']} v{manifest['project']['version']}")
    runpy.run_path(entry, run_name="__main__")
