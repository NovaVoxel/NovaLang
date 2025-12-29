#!/usr/bin/env python3
import os
import shutil

# Import helper scripts from install/
from install.make_cli import make_cli_scripts
from install.paths import get_install_path

def main():
    print("🔧 Installing Nova Language CLI...")

    build_dir = "PATH"
    make_cli_scripts(build_dir)

    target = get_install_path()
    os.makedirs(target, exist_ok=True)

    for name in ("nova", "novac"):
        src = os.path.join(build_dir, name)
        dst = os.path.join(target, name)
        shutil.copy(src, dst)
        print(f"✔ Installed {name} → {dst}")

    print("\n✨ Nova Language erfolgreich installiert!")
    print("   Du kannst jetzt verwenden:")
    print("      novac <file.nova>")
    print("      nova -nomc file.nomc")
    print("      nova -novar file.novar")

if __name__ == "__main__":
    main()
