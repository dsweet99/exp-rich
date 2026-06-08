"""Stdlib-only LogRender registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_log_render_class: Optional[Type[Any]] = None


def register_log_render(log_render_class: Type[Any]) -> None:
    global _log_render_class
    _log_render_class = log_render_class


def log_render_class() -> Type[Any]:
    if _log_render_class is None:
        raise RuntimeError("LogRender not registered; import rich._log_render first")
    return _log_render_class
