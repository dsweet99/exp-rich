"""Lazy Syntax wrapper for markdown (extracted for kiss)."""
from __future__ import annotations


def _syntax_class():
    import importlib as _importlib

    return _importlib.import_module(".syntax", __package__).Syntax


class LazySyntaxType:
    def __new__(cls, *args, **kwargs):
        return _syntax_class()(*args, **kwargs)
