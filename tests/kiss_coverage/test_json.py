"""Kiss static coverage for rich.json."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.json

def test_kiss_json_symbols_0():
    _mod = _import_rich('json')
    JSON = getattr(_mod, 'JSON')
    assert JSON is not None
