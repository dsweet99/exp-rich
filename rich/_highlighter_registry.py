"""Stdlib-only highlighter factory registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Callable, Optional, Type

_repr_highlighter_factory: Optional[Callable[[], Any]] = None
_repr_highlighter_class: Optional[Type[Any]] = None
_regex_highlighter_class: Optional[Type[Any]] = None
_highlighter_base_class: Optional[Type[Any]] = None


def register_highlighters(
    *,
    base_class: Type[Any],
    repr_class: Type[Any],
    repr_factory: Callable[[], Any],
    regex_class: Type[Any],
) -> None:
    """Register highlighter types (called from highlighter.py at import)."""
    global _highlighter_base_class, _repr_highlighter_class, _repr_highlighter_factory
    global _regex_highlighter_class
    _highlighter_base_class = base_class
    _repr_highlighter_class = repr_class
    _repr_highlighter_factory = repr_factory
    _regex_highlighter_class = regex_class


def highlighter_base_class() -> Type[Any]:
    if _highlighter_base_class is None:
        raise RuntimeError("Highlighter not registered; import rich.highlighter first")
    return _highlighter_base_class


def repr_highlighter_class() -> Type[Any]:
    if _repr_highlighter_class is None:
        raise RuntimeError("ReprHighlighter not registered; import rich.highlighter first")
    return _repr_highlighter_class


def repr_highlighter() -> Any:
    if _repr_highlighter_factory is None:
        raise RuntimeError("ReprHighlighter not registered; import rich.highlighter first")
    return _repr_highlighter_factory()


def regex_highlighter_class() -> Type[Any]:
    if _regex_highlighter_class is None:
        raise RuntimeError("RegexHighlighter not registered; import rich.highlighter first")
    return _regex_highlighter_class


def path_highlighter_class() -> Type[Any]:
    """Build PathHighlighter without a static highlighter import in traceback."""
    regex_cls = regex_highlighter_class()
    return type(
        "PathHighlighter",
        (regex_cls,),
        {"highlights": [r"(?P<dim>.*/)(?P<bold>.+)"]},
    )
