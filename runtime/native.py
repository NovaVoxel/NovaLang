import builtins
import importlib


def __native__(path: str, *args):
    """
    Executes a Nova wrapper call directly using Python 3.12.
    Example:
        __native__("math.sqrt", 25)
        __native__("os.path.join", "a", "b")
    """

    # Path must contain at least one dot: "<module>.<attribute>"
    if "." not in path:
        raise ValueError(f"Invalid native path: {path!r}")

    module_name, attr_path = path.split(".", 1)

    # ----------------------------------------
    # Builtins (safe access)
    # ----------------------------------------
    if module_name == "builtins":
        if not hasattr(builtins, attr_path):
            raise AttributeError(f"Builtin '{attr_path}' does not exist")
        func = getattr(builtins, attr_path)
        return func(*args)

    # ----------------------------------------
    # Import module
    # ----------------------------------------
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Module '{module_name}' could not be imported: {e}")

    # ----------------------------------------
    # Resolve nested attributes
    # Example: "os.path.join"
    # ----------------------------------------
    obj = module
    for part in attr_path.split("."):
        if not hasattr(obj, part):
            raise AttributeError(f"'{obj.__name__}' has no attribute '{part}'")
        obj = getattr(obj, part)

    # ----------------------------------------
    # Call the resolved object if it is callable
    # ----------------------------------------
    if callable(obj):
        return obj(*args)

    # If the object is not callable but arguments were provided
    if args:
        raise TypeError(f"'{path}' is not callable but arguments were given")

    # Return non-callable attribute (e.g. math.pi)
    return obj
