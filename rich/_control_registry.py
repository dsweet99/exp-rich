"""Stdlib-only Control class registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_control_class: Optional[Type[Any]] = None


def register_control(control_class: Type[Any]) -> None:
    global _control_class
    _control_class = control_class


def control_class() -> Type[Any]:
    if _control_class is None:
        raise RuntimeError("Control not registered; import rich.control first")
    return _control_class
