from typing import Any, Optional
from importlib import import_module

_console: Optional[Any] = None

def get_console() -> Any:
    global _console
    if _console is None:
        Console = import_module("rich.console").Console
        _console = Console()
    return _console
