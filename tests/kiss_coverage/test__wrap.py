"""Kiss static coverage for rich._wrap."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._wrap

def test_kiss__wrap_symbols_0():
    _mod = _import_rich('_wrap')
    divide_line = getattr(_mod, 'divide_line')
    words = getattr(_mod, 'words')
    assert divide_line is not None
    assert words is not None
