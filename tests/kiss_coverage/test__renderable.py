"""Kiss static coverage for rich._renderable."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._renderable

def test_kiss__renderable_symbols_0():
    _mod = _import_rich('_renderable')
    is_renderable = getattr(_mod, 'is_renderable')
    rich_cast = getattr(_mod, 'rich_cast')
    assert is_renderable is not None
    assert rich_cast is not None
