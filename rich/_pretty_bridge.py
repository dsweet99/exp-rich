"""Runtime bridge so console can use Pretty without importing rich.pretty."""

from typing import Any, Callable, Tuple

_pretty_module: Any = None


def register_pretty_module(pretty_module: Any) -> None:
    global _pretty_module
    _pretty_module = pretty_module


def pretty_helpers() -> Tuple[Any, Callable[..., bool]]:
    if _pretty_module is None:
        raise RuntimeError("rich.pretty has not registered the pretty bridge")
    return _pretty_module.Pretty, _pretty_module.is_expandable
