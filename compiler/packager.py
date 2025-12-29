import json
import os


def package(project_name, entry_file, bin_dir="bin", manifest_path="Manifest.json"):
    """
    Creates a minimal Nova package manifest.

    Example:
        package("MyProject", "main.nomc")
    """

    # Ensure bin directory exists
    os.makedirs(bin_dir, exist_ok=True)

    # Full path to entry file
    entry_path = os.path.join(bin_dir, entry_file)

    # Validate entry file exists
    if not os.path.isfile(entry_path):
        raise FileNotFoundError(
            f"Entry file not found: {entry_path}. "
            "Make sure it was compiled before packaging."
        )

    # Build manifest structure
    manifest = {
        "project": {
            "name": project_name,
            "version": "0.1.0"
        },
        "entry": entry_path.replace("\\", "/")  # normalize for cross‑platform
    }

    # Write manifest
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    except Exception as e:
        raise RuntimeError(f"Failed to write manifest: {e}")

    print(f"Created manifest: {manifest_path}")
    return manifest_path
