"""Kiss static coverage for rich.bar."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.bar

def test_kiss_bar_symbols_0():
    _mod = _import_rich('bar')
    Bar = getattr(_mod, 'Bar')
    assert Bar is not None
