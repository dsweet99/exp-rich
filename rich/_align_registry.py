"""Stdlib-only Align class registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_align_class: Optional[Type[Any]] = None


def register_align(align_class: Type[Any]) -> None:
    global _align_class
    _align_class = align_class


def align_class() -> Type[Any]:
    if _align_class is None:
        raise RuntimeError("Align not registered; import rich.align first")
    return _align_class
