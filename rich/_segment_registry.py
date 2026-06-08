"""Stdlib-only Segment class registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_segment_class: Optional[Type[Any]] = None


def register_segment(segment_class: Type[Any]) -> None:
    global _segment_class
    _segment_class = segment_class


def segment_class() -> Type[Any]:
    if _segment_class is None:
        raise RuntimeError("Segment not registered; import rich.segment first")
    return _segment_class
