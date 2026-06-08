"""Stdlib-only Style class registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_style_class: Optional[Type[Any]] = None


def register_style(style_class: Type[Any]) -> None:
    global _style_class
    _style_class = style_class


def style_class() -> Type[Any]:
    if _style_class is None:
        raise RuntimeError("Style not registered; import rich.style first")
    return _style_class
