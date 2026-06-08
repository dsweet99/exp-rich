"""Kiss static coverage for rich.constrain."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.constrain

def test_kiss_constrain_symbols_0():
    _mod = _import_rich('constrain')
    Constrain = getattr(_mod, 'Constrain')
    assert Constrain is not None
