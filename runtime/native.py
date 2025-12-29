import builtins
import importlib

def __native__(path: str, *args):
    """
    Führt einen Nova-Wrapper-Aufruf direkt mit Python 3.12 aus.
    Beispiel: __native__('math.sqrt', 25)
    """
    if "." not in path:
        raise ValueError(f"Ungültiger native-Pfad: {path}")

    module_name, func_name = path.split(".", 1)

    # Builtins
    if module_name == "builtins":
        func = getattr(builtins, func_name)
        return func(*args)

    # Modul import
    module = importlib.import_module(module_name)
    func = getattr(module, func_name)
    return func(*args)
