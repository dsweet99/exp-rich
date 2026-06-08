"""Stdlib-only blend_rgb registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Callable, Optional

_blend_rgb: Optional[Callable[..., Any]] = None


def register_blend_rgb(blend: Callable[..., Any]) -> None:
    global _blend_rgb
    _blend_rgb = blend


def get_blend_rgb() -> Callable[..., Any]:
    if _blend_rgb is None:
        raise RuntimeError("blend_rgb not registered; import rich.color first")
    return _blend_rgb
