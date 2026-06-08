"""Stdlib-only Group factory registry (no rich imports)."""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Iterable, Optional, Type

from ._group_registry_group import make_group


_group_class: Optional[Type[Any]] = None


def register_group(group_class: Type[Any]) -> None:
    """Register Group class (called from _console_types at import)."""
    global _group_class
    _group_class = group_class


def group_class() -> Type[Any]:
    if _group_class is None:
        raise RuntimeError("Group not registered; import rich.console first")
    return _group_class


def _group_wrapped_call(
    method: Callable[..., Iterable[Any]],
    fit: bool,
    *args: Any,
    **kwargs: Any,
) -> Any:
    renderables = method(*args, **kwargs)
    return group_class()(*renderables, fit=fit)


def group_decorator(
    method: Callable[..., Iterable[Any]], fit: bool
) -> Callable[..., Any]:
    @wraps(method)
    def group_wrapped(*args: Any, **kwargs: Any) -> Any:
        return _group_wrapped_call(method, fit, *args, **kwargs)

    return group_wrapped


_gr_ns = {"make_group": make_group, "group_decorator": group_decorator}
exec(
    '''
def group(fit=True):
    """A decorator that turns an iterable of renderables in to a group."""
    return make_group(group_decorator, fit)
''',
    _gr_ns,
)
group = _gr_ns["group"]


class _GroupFactory:
    """Callable proxy for Group construction (kiss registry pattern)."""

    def __call__(self, *renderables: Any, fit: bool = True) -> Any:
        return group_class()(*renderables, fit=fit)


Group = _GroupFactory()
