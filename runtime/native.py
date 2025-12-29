# ============================================
# Nova native bridge + stdlib backend
# --------------------------------------------
# This file implements:
#
#   - __native__(path, *args)
#       → calls Python stdlib functions
#
#   - NOVA_STDLIB
#       → mapping for Nova's "use std/..." modules
#
#   - nova_globals
#       → sys_args, sys_input
#
# This is the backend for Nova's standard library.
# ============================================

import builtins
import importlib
import math
import os
import time
import random
import json

# Injected by launcher.py
try:
    from launcher import nova_globals
except Exception:
    nova_globals = {
        "sys_args": [],
        "sys_input": input,
    }


# --------------------------------------------
# Nova Stdlib Backend
# --------------------------------------------
# These functions are exposed to Nova as:
#
#   use std/math
#   math.sqrt(25)
#
#   use std/os
#   os.listdir(".")
#
#   use std/time
#   time.sleep(1)
#
#   use std/random
#   random.randint(1, 10)
#
#   use std/json
#   json.loads("{...}")
#
# --------------------------------------------

NOVA_STDLIB = {
    # math
    "std/math.sqrt": math.sqrt,
    "std/math.sin": math.sin,
    "std/math.cos": math.cos,
    "std/math.tan": math.tan,
    "std/math.log": math.log,
    "std/math.exp": math.exp,
    "std/math.pi": lambda: math.pi,
    "std/math.e": lambda: math.e,

    # os
    "std/os.getcwd": os.getcwd,
    "std/os.listdir": os.listdir,
    "std/os.exists": os.path.exists,
    "std/os.isfile": os.path.isfile,
    "std/os.isdir": os.path.isdir,
    "std/os.join": os.path.join,

    # time
    "std/time.time": time.time,
    "std/time.sleep": time.sleep,

    # random
    "std/random.random": random.random,
    "std/random.randint": random.randint,
    "std/random.choice": random.choice,

    # json
    "std/json.loads": json.loads,
    "std/json.dumps": json.dumps,
}


# --------------------------------------------
# Native call bridge
# --------------------------------------------
def __native__(path: str, *args):
    """
    Execute a native Python call or access a Python attribute.

    Supports:
        - stdlib calls (std/math.sqrt)
        - python modules (math.sqrt)
        - builtins (builtins.print)
        - nova runtime globals (nova.sys_args)
    """

    # ----------------------------------------
    # Nova runtime globals
    # ----------------------------------------
    if path.startswith("nova."):
        key = path.split(".", 1)[1]
        if key not in nova_globals:
            raise KeyError(f"Nova runtime variable '{key}' does not exist")
        value = nova_globals[key]
        if callable(value):
            return value(*args)
        if args:
            raise TypeError(f"'{path}' is not callable but arguments were given")
        return value

    # ----------------------------------------
    # Nova Stdlib (std/...)
    # ----------------------------------------
    if path in NOVA_STDLIB:
        func = NOVA_STDLIB[path]
        return func(*args)

    # ----------------------------------------
    # Builtins
    # ----------------------------------------
    if path.startswith("builtins."):
        name = path.split(".", 1)[1]
        if not hasattr(builtins, name):
            raise AttributeError(f"Builtin '{name}' does not exist")
        obj = getattr(builtins, name)
        if callable(obj):
            return obj(*args)
        if args:
            raise TypeError(f"'{path}' is not callable but arguments were given")
        return obj

    # ----------------------------------------
    # Python module import fallback
    # ----------------------------------------
    if "." not in path:
        raise ValueError(f"Invalid native path: {path!r}")

    module_name, attr_path = path.split(".", 1)

    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Module '{module_name}' could not be imported: {e}")

    obj = module
    for part in attr_path.split("."):
        if not hasattr(obj, part):
            raise AttributeError(f"'{obj}' has no attribute '{part}'")
        obj = getattr(obj, part)

    if callable(obj):
        return obj(*args)

    if args:
        raise TypeError(f"'{path}' is not callable but arguments were given")

    return obj
