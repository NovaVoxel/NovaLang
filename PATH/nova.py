# nova.py — Nova CLI wrapper
# This file goes into PATH and only forwards commands to the real launcher.

import sys
import subprocess
import os

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  nova -nomc <file.nomc>")
        print("  nova -novar <file.novar>")
        sys.exit(1)

    mode = sys.argv[1]
    path = sys.argv[2]

    # Path to the real runtime executable
    # After Nuitka build: nova-runtime.exe (or just "nova-runtime" on Linux)
    runtime_exe = os.path.join(os.path.dirname(__file__), "nova-runtime")

    # Windows compatibility
    if os.name == "nt":
        runtime_exe += ".exe"

    if not os.path.exists(runtime_exe):
        print(f"Error: runtime executable not found: {runtime_exe}")
        sys.exit(1)

    # Forward the call to the runtime
    cmd = [runtime_exe, mode, path] + sys.argv[3:]

    try:
        result = subprocess.call(cmd)
        sys.exit(result)
    except Exception as e:
        print(f"Failed to launch runtime: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
