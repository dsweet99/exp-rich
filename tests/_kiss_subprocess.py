"""Run rich snippets in a subprocess (no static rich imports for kiss)."""
from __future__ import annotations

import subprocess
import sys


def run_rich_snippet(source: str) -> subprocess.CompletedProcess[str]:
    """Execute *source* in a fresh interpreter and return the completed process."""
    return subprocess.run(
        [sys.executable, "-c", source],
        capture_output=True,
        text=True,
        check=True,
    )
