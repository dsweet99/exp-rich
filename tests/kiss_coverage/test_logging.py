"""Kiss static coverage for rich.logging."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.logging

def test_kiss_logging_symbols_0():
    _mod = _import_rich('logging')
    RichHandler = getattr(_mod, 'RichHandler')
    assert RichHandler is not None
