"""Kiss static coverage for rich.repr."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.repr

def test_kiss_repr_symbols_0():
    _mod = _import_rich('repr')
    ReprError = getattr(_mod, 'ReprError')
    auto = getattr(_mod, 'auto')
    rich_repr = getattr(_mod, 'rich_repr')
    assert ReprError is not None
    assert auto is not None
    assert rich_repr is not None
