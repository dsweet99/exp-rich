"""Kiss static coverage for rich.filesize."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.filesize

def test_kiss_filesize_symbols_0():
    _mod = _import_rich('filesize')
    decimal = getattr(_mod, 'decimal')
    pick_unit_and_suffix = getattr(_mod, 'pick_unit_and_suffix')
    assert decimal is not None
    assert pick_unit_and_suffix is not None
