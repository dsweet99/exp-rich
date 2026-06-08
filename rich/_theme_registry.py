"""Stdlib-only theme factory registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_theme_class: Optional[Type[Any]] = None


def register_theme(theme_class: Type[Any]) -> None:
    """Register Theme class (called from theme.py at import)."""
    global _theme_class
    _theme_class = theme_class


def theme_class() -> Type[Any]:
    if _theme_class is None:
        raise RuntimeError("Theme not registered; import rich.theme first")
    return _theme_class
