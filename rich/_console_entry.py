"""Thin Console entry point without static rich.console import (kiss decoupling)."""
from __future__ import annotations

import importlib as _importlib
from typing import Any, Optional, Type

from ._align_types import OverflowMethod
from ._console_dimensions import ConsoleDimensions
from ._console_types import (
    CaptureError,
    ConsoleOptions,
    Group,
    RenderResult,
    RenderableType,
    ScreenUpdate,
)
from ._group_registry import group

_console_class: Optional[Type[Any]] = None


def register_console_class(cls: Type[Any]) -> None:
    """Register Console class (called from console.py at import)."""
    global _console_class
    _console_class = cls


def console_class() -> Type[Any]:
    """Return the Console class, loading rich.console lazily if needed."""
    global _console_class
    if _console_class is None:
        _console_class = _importlib.import_module(".console", __package__).Console
    return _console_class


class _ConsoleFactory:
    """Callable proxy for Console construction."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return console_class()(*args, **kwargs)


Console = _ConsoleFactory()

__all__ = [
    "CaptureError",
    "Console",
    "ConsoleDimensions",
    "ConsoleOptions",
    "Group",
    "OverflowMethod",
    "RenderResult",
    "RenderableType",
    "ScreenUpdate",
    "console_class",
    "group",
    "register_console_class",
]
