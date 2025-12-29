import os
from detect_os import get_os

def get_install_path():
    osname = get_os()

    if osname == "windows":
        return os.path.expandvars(r"%USERPROFILE%\AppData\Local\Microsoft\WindowsApps")

    if osname in ("linux", "macos"):
        return os.path.expanduser("~/.local/bin")

    raise RuntimeError("Unsupported OS")
