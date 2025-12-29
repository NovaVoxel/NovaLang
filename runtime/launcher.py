# ============================================
# Nova launcher
# Executes .novar archives directly (like a JAR)
# ============================================

import sys
import tarfile
import json
import ctypes
from llvmlite import binding

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()


class NovaLauncherError(Exception):
    """Generic launcher error for Nova runtime."""
    pass


# ----------------------------------------
# Global runtime variables for Nova
# ----------------------------------------
nova_globals = {
    # Command-line arguments AFTER the .novar path
    "sys_args": sys.argv[2:],  # argv[0] = exe, argv[1] = .novar, rest = user args
    # Direct access to input()
    "sys_input": input,
}


def load_nomc_from_bytes(obj_bytes: bytes):
    """
    Load a .nomc module into an MCJIT execution engine.

    NOTE:
        Depending on how you emit .nomc, you might need to switch between:
          - parse_bitcode()  -> for LLVM bitcode
          - parse_assembly() -> for textual .ll
          - create_object_file() -> for native object files

        This implementation assumes that .nomc is LLVM bitcode.
    """
    try:
        backing_mod = binding.parse_bitcode(obj_bytes)
    except Exception as e:
        raise NovaLauncherError(f"Failed to parse .nomc bitcode: {e}")

    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine(opt=3)

    try:
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        engine.finalize_object()
        engine.run_static_constructors()
    except Exception as e:
        raise NovaLauncherError(f"Failed to initialize execution engine: {e}")

    return engine


def run_main(engine, module_name: str) -> int:
    """
    Execute main() from a loaded module.

    Convention:
        Nova codegen must emit a C-style entry:
            int main(void);
    """
    try:
        func_ptr = engine.get_function_address("main")
    except Exception:
        raise NovaLauncherError(f"Module '{module_name}' has no main() function")

    if func_ptr == 0:
        raise NovaLauncherError(f"main() not found in module '{module_name}'")

    cfunc = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)
    return cfunc()


def launch(novar_path: str) -> int:
    """
    Launch a .novar archive:
      - open tar
      - read Manifest.json
      - load and execute all listed .nomc binaries
    """
    # ----------------------------------------
    # Open .novar archive
    # ----------------------------------------
    try:
        tar = tarfile.open(novar_path, "r")
    except Exception as e:
        raise NovaLauncherError(f"Failed to open .novar '{novar_path}': {e}")

    with tar:
        # ----------------------------------------
        # Read manifest
        # ----------------------------------------
        try:
            manifest_file = tar.extractfile("bin/Manifest.json")
            if manifest_file is None:
                raise NovaLauncherError("Manifest 'bin/Manifest.json' not found in archive")
            manifest = json.load(manifest_file)
        except Exception as e:
            raise NovaLauncherError(f"Failed to read Manifest.json: {e}")

        project = manifest.get("project", {})
        name = project.get("name", "<unknown>")
        version = project.get("version", "<unknown>")

        print(f"Launching {name} v{version}")

        binaries = manifest.get("bin", [])
        if not binaries:
            raise NovaLauncherError("Manifest contains no compiled binaries in 'bin'")

        # ----------------------------------------
        # Load and execute each .nomc module
        # ----------------------------------------
        last_result = 0

        for nomc_file in binaries:
            try:
                f = tar.extractfile(nomc_file)
                if f is None:
                    raise NovaLauncherError(f"Binary '{nomc_file}' not found in archive")
                obj_bytes = f.read()
            except Exception as e:
                raise NovaLauncherError(f"Failed to read '{nomc_file}': {e}")

            print(f"  -> Loading {nomc_file}...")
            engine = load_nomc_from_bytes(obj_bytes)

            # Execute main()
            try:
                result = run_main(engine, nomc_file)
                print(f"     main() returned {result}")
                last_result = result
            except NovaLauncherError as e:
                print(f"     Runtime error in {nomc_file}: {e}")
                last_result = 1

        return last_result


def main():
    if len(sys.argv) < 2:
        print("Usage: nova <file.novar> [args...]")
        sys.exit(1)

    novar_path = sys.argv[1]

    try:
        exit_code = launch(novar_path)
    except NovaLauncherError as e:
        print(f"[NovaLauncherError] {e}")
        sys.exit(1)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
