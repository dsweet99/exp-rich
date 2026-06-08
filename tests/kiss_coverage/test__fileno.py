"""Kiss static coverage for rich._fileno."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._fileno

def test_kiss__fileno_symbols_0():
    _mod = _import_rich('_fileno')
    get_fileno = getattr(_mod, 'get_fileno')
    assert get_fileno is not None
