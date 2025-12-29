# NovAr Format Specification

NovAr (`.novar`) is the official package format for the Nova language.  
It bundles compiled Nova Machine Code (`.nomc`) together with metadata and optional resources, similar to how JAR files work in Java.

---

## 📂 Archive Type
- **Base format:** TAR (uncompressed, for fast loading)
- **Optional:** GZ compression (`.novar.gz`) if size reduction is required
- **Execution model:** The archive is executed directly without extraction

---

## 📂 Directory Layout


bin/                # compiled Nova Machine Code Manifest.json     # project metadata .nomc     # native machine code files lib/                # optional shared libraries res/                # optional resources (images, audio, data)


---

## 📂 Manifest.json
```json
{
  "project": {
    "name": "MyNovaApp",
    "version": "1.0.0",
    "author": "Vincent Noll"
  },
  "entry": "bin/main.nomc",
  "bin": [
    "bin/main.nomc",
    "bin/utils.nomc"
  ],
  "requires": [
    "stdlib/math",
    "stdlib/io"
  ],
  "format_version": "1.0"
}
```

Fields

- **project** → metadata (name, version, author)
- **entry** → main executable .nomc file
- **bin** → list of compiled binaries
- **requires** → optional list of stdlib modules
- **format_version** → NovAr format version


---

📂 Execution Model

1. Launcher opens .novar directly (no extraction).
2. Reads Manifest.json to locate the entry.
3. Loads the .nomc file into memory.
4. Executes main() via LLVM MCJIT or native loader.
5. Additional .nomc files in bin/ can be dynamically loaded at runtime.


---

✨ Advantages

• Single file distribution → one .novar contains everything
• No extraction → runs directly from archive
• Fast startup → uncompressed TAR + memory‑mapped loading
• Future‑proof → lib/ and res/ directories for extensions


---

📂 Example Project Structure

MyNovaApp/
  nova/
    main.nova
    utils.nova
  bin/
    main.nomc
    utils.nomc
    Manifest.json
  target/
    MyNovaApp.novar


---

📂 Versioning

• NovAr format version: 1.0
• Backwards compatibility guaranteed for minor updates
• Major changes will increment the format version in Manifest.json


---

📂 Summary

NovAr (.novar) is the official executable archive format for Nova.
It ensures fast, portable, and self‑contained distribution of Nova applications, optimized with LTO and direct archive execution.
