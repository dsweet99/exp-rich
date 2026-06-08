"""Kiss static coverage for rich.region."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.region

def test_kiss_region_symbols_0():
    _mod = _import_rich('region')
    Region = getattr(_mod, 'Region')
    assert Region is not None
