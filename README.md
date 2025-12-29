# Nova Language

Nova is a next‑generation programming language designed for **Python‑like simplicity** and **C‑level speed**.  
It compiles directly to **Nova Machine Code (.nomc)** and packages applications into **NovAr archives (.novar)** for fast, portable distribution.

---

## ✨ Features
- **Native speed**: LLVM backend with `-O3` and LTO optimizations
- **No VM**: Nova compiles directly to `.nomc` machine code
- **NovAr format**: single‑file executable archives, similar to JAR
- **Modular IR**: clean intermediate representation for extensibility
- **Cross‑platform**: runs on x86, ARM, and more

---

## 📂 Project Structure

```
nova/        # source files (.nova) bin/         # compiled machine code (.nomc) + Manifest.json target/      # packaged NovAr archives
(.novar) compiler/    # lexer, parser, IR, codegen, novar builder runtime/     # launcher and native intrinsics
```

---

## 🚀 Getting Started

### Build
```bash
python build.py


This compiles all .nova files in nova/ into .nomc binaries in bin/
and packages them into target/<project>.novar.

Run

nova -jar target/MyNovaApp.novar
```

The launcher executes .novar directly without extraction.

---

📦 NovAr Format

See NovArFormat.md for the full specification.
In short: .novar archives contain bin/*.nomc and Manifest.json and are executed directly.

---

📜 License

MIT
