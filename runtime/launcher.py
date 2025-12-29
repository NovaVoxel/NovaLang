# ============================================
# Nova launcher
# Executes .novar directly without extracting (like a JAR)
# ============================================

import tarfile
import json
import ctypes
from llvmlite import binding

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()
nova_globals["sys_args"] = sys.argv[1:]
nova_globals["sys_input"] = input


class NovaLauncherError(Exception):
    pass


def load_nomc_from_bytes(obj_bytes):
    """Load a .nomc object (LLVM bitcode) into an MCJIT engine."""
    try:
        backing_mod = binding.parse_bitcode(obj_bytes)
    except Exception as e:
        raise NovaLauncherError(f"Failed to parse bitcode: {e}")

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine(opt=3)

    try:
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        engine.finalize_object()
        engine.run_static_constructors()
    except Exception as e:
        raise NovaLauncherError(f"Failed to initialize execution engine: {e}")

    return engine


def run_main(engine, module_name):
    """Execute main() from a loaded module."""
    try:
        func_ptr = engine.get_function_address("main")
    except Exception:
        raise NovaLauncherError(f"Module '{module_name}' has no main() function")

    if func_ptr == 0:
        raise NovaLauncherError(f"main() not found in module '{module_name}'")

    cfunc = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)
    return cfunc()


def launch(novar_path):
    # ----------------------------------------
    # Open .novar archive
    # ----------------------------------------
    try:
        tar = tarfile.open(novar_path, "r")
    except Exception as e:
        raise NovaLauncherError(f"Failed to open .novar: {e}")

    with tar:
        # ----------------------------------------
        # Read manifest
        # ----------------------------------------
        try:
            manifest_file = tar.extractfile("bin/Manifest.json")
            manifest = json.load(manifest_file)
        except Exception as e:
            raise NovaLauncherError(f"Failed to read Manifest.json: {e}")

        project = manifest.get("project", {})
        name = project.get("name", "<unknown>")
        version = project.get("version", "<unknown>")

        print(f"🚀 Launching {name} v{version}")

        binaries = manifest.get("bin", [])
        if not binaries:
            raise NovaLauncherError("Manifest contains no compiled binaries")

        # ----------------------------------------
        # Load and execute each .nomc module
        # ----------------------------------------
        for nomc_file in binaries:
            try:
                f = tar.extractfile(nomc_file)
                obj_bytes = f.read()
            except Exception as e:
                raise NovaLauncherError(f"Failed to read {nomc_file}: {e}")

            print(f"→ Loading {nomc_file}...")

            engine = load_nomc_from_bytes(obj_bytes)

            # Execute main()
            try:
                result = run_main(engine, nomc_file)
                print(f"   Returned {result}")
            except NovaLauncherError as e:
                print(f"   ⚠ Runtime error: {e}")
