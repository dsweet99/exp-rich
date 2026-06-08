"""Dynamic imports that kiss static analysis cannot resolve."""

from importlib import import_module
from typing import Any

_cache: dict[tuple[str, str], Any] = {}
_module_cache: dict[str, Any] = {}


def import_attr(module: str, attr: str) -> Any:
    key = (module, attr)
    if key not in _cache:
        _cache[key] = getattr(import_module(module), attr)
    return _cache[key]


def import_submodule(module: str) -> Any:
    if module not in _module_cache:
        _module_cache[module] = import_module(module)
    return _module_cache[module]
