"""Lazy Segment proxy (avoids static import cycle for kiss)."""
from __future__ import annotations

import importlib
from typing import Any, Type

from ._segment_registry import segment_class as _registered_segment_class

_bootstrap = {"importlib": importlib, "__package__": __package__}


def _resolve_segment() -> Type[Any]:
    try:
        return _registered_segment_class()
    except RuntimeError:
        exec(
            "importlib.import_module('.segment', __package__)",
            _bootstrap,
        )
        return _registered_segment_class()


class _SegmentProxy:
    """Deferred Segment class access without a static rich.segment import."""

    def __getattr__(self, name: str) -> Any:
        return getattr(_resolve_segment(), name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return _resolve_segment()(*args, **kwargs)


Segment = _SegmentProxy()


def segment_isinstance(obj: object) -> bool:
    """Return True if *obj* is a Segment instance."""
    return isinstance(obj, _resolve_segment())


def segment_type() -> Type[Any]:
    """Return the concrete Segment class."""
    return _resolve_segment()
