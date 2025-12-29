import os
import stat

def make_cli_scripts(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # novac
    with open(os.path.join(output_dir, "novac"), "w") as f:
        f.write("#!/usr/bin/env python3\nfrom tools.novac import main\nmain()\n")

    # nova
    with open(os.path.join(output_dir, "nova"), "w") as f:
        f.write("#!/usr/bin/env python3\nfrom tools.nova import main\nmain()\n")

    # executable flags
    for name in ("novac", "nova"):
        path = os.path.join(output_dir, name)
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)
