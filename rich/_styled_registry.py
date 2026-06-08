"""Stdlib-only Styled class registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_styled_class: Optional[Type[Any]] = None


def register_styled(styled_class: Type[Any]) -> None:
    global _styled_class
    _styled_class = styled_class


def styled_class() -> Type[Any]:
    if _styled_class is None:
        raise RuntimeError("Styled not registered; import rich.styled first")
    return _styled_class
