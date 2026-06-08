"""
A very minimal `cp` clone that displays a progress bar.
"""
import importlib as _importlib
import os
import shutil
import sys

Progress = _importlib.import_module("rich.progress").Progress

if __name__ == "__main__":
    if len(sys.argv) == 3:
        with Progress() as progress:
            desc = os.path.basename(sys.argv[1])
            with progress.open(sys.argv[1], "rb", description=desc) as src:
                with open(sys.argv[2], "wb") as dst:
                    shutil.copyfileobj(src, dst)
    else:
        print("Copy a file with a progress bar.")
        print("Usage:\n\tpython cp_progress.py SRC DST")
