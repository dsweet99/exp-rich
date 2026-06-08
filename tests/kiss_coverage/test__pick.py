"""Kiss static coverage for rich._pick."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._pick

def test_kiss__pick_symbols_0():
    _mod = _import_rich('_pick')
    pick_bool = getattr(_mod, 'pick_bool')
    assert pick_bool is not None
