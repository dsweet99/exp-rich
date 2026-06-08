"""Kiss static coverage for rich._loop."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._loop

def test_kiss__loop_symbols_0():
    _mod = _import_rich('_loop')
    loop_first = getattr(_mod, 'loop_first')
    loop_first_last = getattr(_mod, 'loop_first_last')
    loop_last = getattr(_mod, 'loop_last')
    assert loop_first is not None
    assert loop_first_last is not None
    assert loop_last is not None
