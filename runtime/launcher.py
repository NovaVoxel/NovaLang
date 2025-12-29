# Nova launcher
# Executes .novar directly without extracting (like a JAR)

import tarfile, io, json
from llvmlite import binding

binding.initialize()
binding.initialize_native_target()
binding.initialize_native_asmprinter()

def launch(novar_path):
    # Open .novar archive
    with tarfile.open(novar_path, "r") as tar:
        # Read manifest directly from archive
        manifest_file = tar.extractfile("bin/Manifest.json")
        manifest = json.load(manifest_file)

        print(f"Launching {manifest['project']['name']} v{manifest['project']['version']}")

        # Iterate over compiled .nomc binaries inside archive
        for nomc_file in manifest["bin"]:
            f = tar.extractfile(nomc_file)
            obj_bytes = f.read()

            # Load machine code into memory and execute
            target = binding.Target.from_default_triple()
            target_machine = target.create_target_machine(opt=3)
            backing_mod = binding.parse_bitcode(obj_bytes)
            engine = binding.create_mcjit_compiler(backing_mod, target_machine)

            engine.finalize_object()
            engine.run_static_constructors()

            # Run main() from the loaded module
            func_ptr = engine.get_function_address("main")
            import ctypes
            cfunc = ctypes.CFUNCTYPE(ctypes.c_int)(func_ptr)
            result = cfunc()
            print(f"→ {nomc_file} returned {result}")
