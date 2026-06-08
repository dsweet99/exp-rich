"""Stdlib-only deferred class access (no rich imports)."""
from __future__ import annotations

from typing import Any, Callable


class DeferredType:
    """Resolve a class on first use via a zero-argument factory."""

    def __init__(self, factory: Callable[[], type]) -> None:
        self._factory = factory

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._factory()(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._factory(), name)
