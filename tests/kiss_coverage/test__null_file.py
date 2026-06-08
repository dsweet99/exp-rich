"""Kiss static coverage for rich._null_file."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._null_file

def test_kiss__null_file_symbols_0():
    _mod = _import_rich('_null_file')
    NullFile = getattr(_mod, 'NullFile')
    assert NullFile is not None
