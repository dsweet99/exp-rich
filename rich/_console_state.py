from __future__ import annotations

import os
from typing import Any, Callable, Optional
from ._render_protocol import Console

try:
    IMPORT_CWD = os.path.abspath(os.getcwd())
except FileNotFoundError:
    IMPORT_CWD = ""

_console: Optional[Any] = None
_console_factory: Optional[Callable[[], Any]] = None

def register_console_factory(factory: Callable[[], "Console"]) -> None:
    """Register the callable used to construct the shared console."""
    global _console_factory
    _console_factory = factory

def obtain_shared_console() -> "Console":
    """Create or return the module-level shared console instance."""
    global _console
    if _console is None:
        if _console_factory is None:
            raise RuntimeError("Console factory not registered; import rich first")
        _console = _console_factory()
    return _console
