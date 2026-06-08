"""Kiss static coverage for rich._extension."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._extension

def test_kiss__extension_symbols_0():
    _mod = _import_rich('_extension')
    load_ipython_extension = getattr(_mod, 'load_ipython_extension')
    assert load_ipython_extension is not None
