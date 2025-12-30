#!/usr/bin/env python3
import os
import shutil
import sys

# Import helper scripts from install/
from install.make_cli import make_cli_scripts
from install.paths import get_install_path

def resolve_binary(build_dir: str, name: str) -> str:
    """
    Find the correct binary depending on OS and Nuitka output:
      - Windows: name.exe
      - Linux:   name-linux
      - Fallback: name (if already renamed)
    """
    candidates = [
        f"{name}.exe",     # Windows
        f"{name}-linux",   # Linux
        name               # fallback
    ]

    for c in candidates:
        path = os.path.join(build_dir, c)
        if os.path.exists(path):
            return path

    print(f"❌ Fehler: Konnte Binary für '{name}' nicht finden.")
    sys.exit(1)


def main():
    print("🔧 Installing Nova Language CLI...")

    build_dir = "PATH"
    make_cli_scripts(build_dir)

    target = get_install_path()
    os.makedirs(target, exist_ok=True)

    for name in ("nova", "novac"):
        src = resolve_binary(build_dir, name)
        dst = os.path.join(target, name)

        # Ensure destination is executable name without extension
        shutil.copy(src, dst)
        print(f"✔ Installed {name} → {dst}")

    print("\n✨ Nova Language erfolgreich installiert!")
    print("   Du kannst jetzt verwenden:")
    print("      novac <file.nova>")
    print("      nova -nomc file.nomc")
    print("      nova -novar file.novar")


if __name__ == "__main__":
    main()
