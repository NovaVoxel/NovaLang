import platform

def get_os():
    system = platform.system().lower()
    if "windows" in system:
        return "windows"
    if "linux" in system:
        return "linux"
    if "darwin" in system or "mac" in system:
        return "macos"
    return "unknown"
