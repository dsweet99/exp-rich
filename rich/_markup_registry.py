"""Stdlib-only markup render registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Callable, Optional

_render_markup: Optional[Callable[..., Any]] = None


def register_render_markup(render: Callable[..., Any]) -> None:
    global _render_markup
    _render_markup = render


def get_render_markup() -> Callable[..., Any]:
    if _render_markup is None:
        raise RuntimeError("markup.render not registered; import rich.markup first")
    return _render_markup
