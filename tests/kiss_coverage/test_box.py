"""Kiss static coverage for rich.box."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.box

def test_kiss_box_symbols_0():
    _mod = _import_rich('box')
    Box = getattr(_mod, 'Box')
    assert Box is not None
