import json

def launch():
    with open("Manifest.json") as f:
        manifest = json.load(f)
    entry = manifest["entry"]
    print(f"Launching {manifest['project']['name']} v{manifest['project']['version']}")
    with open(entry) as f:
        code = f.read()
        print("Executing NOMC:\n", code)
