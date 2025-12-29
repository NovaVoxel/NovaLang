# Introduction

Nova is a minimalist, fast programming language with Python‑like syntax and C/C++‑level performance.
It compiles .nova source files into native `.nomc` binaries and packages them into `.novar` archives for cross‑platform distribution.

---

## Project Structure
```
nova/        # Source files (.nova)
stdlib/      # Standard library (.nova)
bin/         # Compiled modules (.nomc)
target/      # Final packages (.novar)
compiler/    # Compiler sources (Lexer, Parser, IR, Codegen)
build.py     # Build script
native.py    # Bridge to Python/C/LLVM
```

---

## Building

1. Place your `.nova` files in the nova/ directory.
2. Run the build:python3 build.py
3. Output:
- `.nomc` files in bin/
- `.novar` archive in target/



---

## NovAr Format

A `.novar` archive contains:

- `bin/*.nomc` → platform‑specific binaries
- `Manifest.json` → metadata, entry point, targets


## Example Manifest:
```json
{
  "name": "NovaProject",
  "entry": "main.nomc",
  "targets": {
    "linux-x86_64": "bin/main-linux.nomc",
    "windows-x86_64": "bin/main-win.nomc",
    "macos-arm64": "bin/main-macos.nomc"
  }
}
```

---

## Using the Stdlib

Import modules with use `std/<module>`.
Examples:

Math
```nova
use std/math

func main() {
    print("sqrt(9) = " + sqrt(9))
}
```

## Networking
```nova
use std/net

func main() {
    let server = listen("0.0.0.0", 25565)
    let client = accept(server)
    write(client, "Hello from Nova!")
}
```

## Graphics
```nova
use std/gfx

func main() {
    let win = create_window("Demo", 800, 600)

    func loop() {
        clear(win, "black")
        draw_rect(win, 100, 100, 200, 150, "red")
        draw_text(win, "Hello Nova!", 120, 120, "white")
    }

    run(win, loop)
}
```

## QoL (Files, Time, CLI)
```nova
use std/fs
use std/time
use std/cli

func main() {
    write_file("log.txt", "Nova started")
    print("Now: " + now())
    let name = prompt("Enter your name: ")
    print("Hello " + name)
}
```

---

## Debugging

- Syntax errors are reported via `issues.py` (line/column).
- `debug.py` can generate AST/IR dumps.
- If the build succeeds, output stays silent except for a ✅ success message.


---

## Best Practices

- Modularize: split code into multiple `.nova` files.
- Use the Stdlib: avoid reinventing helpers if modules already exist.
- Cross‑compile: generate .nomc for multiple platforms and package them into .novar.
- Document: provide `README.md` and `HowToUse.md` for clear onboarding.
