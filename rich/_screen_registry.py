"""Stdlib-only screen factory registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_screen_class: Optional[Type[Any]] = None


def register_screen(screen_class: Type[Any]) -> None:
    """Register Screen class (called from screen.py at import)."""
    global _screen_class
    _screen_class = screen_class


def screen_class() -> Type[Any]:
    if _screen_class is None:
        raise RuntimeError("Screen not registered; import rich.screen first")
    return _screen_class
