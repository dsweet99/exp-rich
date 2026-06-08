"""Stdlib-only render protocol type aliases (no rich imports)."""
from __future__ import annotations

from typing import Any, Iterable, Protocol, TypeAlias, runtime_checkable

Console: TypeAlias = Any
StyleType: TypeAlias = Any
Text: TypeAlias = Any
Table: TypeAlias = Any
Control: TypeAlias = Any
ConsoleOptions: TypeAlias = Any
RenderableType: TypeAlias = Any
RenderResult: TypeAlias = Iterable[Any]


@runtime_checkable
class ConsoleRenderable(Protocol):
    """Minimal console renderable protocol for static analysis."""

    def __rich_console__(self, console: Any, options: Any) -> RenderResult: ...


@runtime_checkable
class RenderHook(Protocol):
    """Minimal render hook protocol for static analysis."""

    def process_renderables(self, renderables: list[Any]) -> list[Any]: ...
