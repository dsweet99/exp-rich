"""Stdlib-only renderable factories (no rich imports)."""
from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, Type

_table_grid_factory: Optional[Callable[..., Any]] = None
_renderables_factory: Optional[Type[Any]] = None


def register_table_grid(factory: Callable[..., Any]) -> None:
    global _table_grid_factory
    _table_grid_factory = factory


def register_renderables(renderables_class: Type[Any]) -> None:
    global _renderables_factory
    _renderables_factory = renderables_class


def table_grid(*args: Any, **kwargs: Any) -> Any:
    if _table_grid_factory is None:
        raise RuntimeError("Table.grid factory not registered; import rich.table first")
    return _table_grid_factory(*args, **kwargs)


def renderables(items: Optional[Iterable[Any]] = None) -> Any:
    if _renderables_factory is None:
        raise RuntimeError("Renderables class not registered; import rich.containers first")
    return _renderables_factory(items)
