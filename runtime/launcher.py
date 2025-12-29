import json

def execute_nomc(code: str):
    """
    Minimaler NOMC-Interpreter:
    Liest Zeilen wie 'FUNC main' und ruft die passende Funktion.
    """
    lines = code.strip().splitlines()
    for line in lines:
        parts = line.split()
        if parts[0] == "FUNC":
            func_name = parts[1]
            if func_name == "main":
                nova_main()

def nova_main():
    # Hier kannst du Builtins oder Stdlib-Funktionen direkt aufrufen
    print("Hello from Nova main()")

def launch():
    with open("Manifest.json") as f:
        manifest = json.load(f)
    entry = manifest["entry"]

    print(f"Launching {manifest['project']['name']} v{manifest['project']['version']}")

    with open(entry) as f:
        code = f.read()

    execute_nomc(code)

if __name__ == "__main__":
    launch()
