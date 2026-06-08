"""Kiss static coverage for rich._timer."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._timer

def test_kiss__timer_symbols_0():
    _mod = _import_rich('_timer')
    timer = getattr(_mod, 'timer')
    assert timer is not None
