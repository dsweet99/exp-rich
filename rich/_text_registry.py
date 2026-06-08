"""Stdlib-only Text class registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_text_class: Optional[Type[Any]] = None


def register_text(text_class: Type[Any]) -> None:
    global _text_class
    _text_class = text_class


def get_text_class() -> Type[Any]:
    if _text_class is None:
        raise RuntimeError("Text not registered; import rich.text first")
    return _text_class
