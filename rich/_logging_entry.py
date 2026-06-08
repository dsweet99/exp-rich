"""Thin RichHandler entry (kiss decoupling)."""
from __future__ import annotations

import importlib as _importlib
from typing import Any, Optional, Type

_handler_class: Optional[Type[Any]] = None


def register_rich_handler_class(cls: Type[Any]) -> None:
    global _handler_class
    _handler_class = cls


def rich_handler_class() -> Type[Any]:
    global _handler_class
    if _handler_class is None:
        _handler_class = _importlib.import_module(".logging", __package__).RichHandler
    return _handler_class


class _RichHandlerFactory:
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return rich_handler_class()(*args, **kwargs)


RichHandler = _RichHandlerFactory()
