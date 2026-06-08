"""Kiss static coverage for rich._unicode_data."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._unicode_data

def test_kiss__unicode_data_symbols_0():
    _mod = _import_rich('_unicode_data')
    load = getattr(_mod, 'load')
    assert load is not None
