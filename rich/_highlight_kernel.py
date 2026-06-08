"""Stdlib-only highlight helpers (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_text_class: Optional[Type[Any]] = None
_span_class: Optional[Type[Any]] = None


def register_text_types(text_class: Type[Any], span_class: Type[Any]) -> None:
    """Register Text and Span classes (called from text.py at import)."""
    global _text_class, _span_class
    _text_class = text_class
    _span_class = span_class


def text_class() -> Type[Any]:
    if _text_class is None:
        raise RuntimeError("Text class not registered; import rich.text first")
    return _text_class


def span_class() -> Type[Any]:
    if _span_class is None:
        raise RuntimeError("Span class not registered; import rich.text first")
    return _span_class


def is_text_instance(obj: object) -> bool:
    if _text_class is not None and isinstance(obj, _text_class):
        return True
    return hasattr(obj, "copy") and hasattr(obj, "plain") and hasattr(
        obj, "highlight_regex"
    )


def make_text(value: str) -> Any:
    return text_class()(value)
