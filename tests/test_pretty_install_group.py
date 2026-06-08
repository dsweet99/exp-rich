"""Dedicated kiss coverage for rich.pretty.install (import + call)."""
from __future__ import annotations

import sys
from io import StringIO

from rich.pretty import install


def test_pretty_install_import_and_call():
    from rich._console_entry import Console

    console = Console(file=StringIO(), force_terminal=False)
    old_hook = sys.displayhook
    try:
        install(console=console)
        assert sys.displayhook is not old_hook
    finally:
        sys.displayhook = old_hook
