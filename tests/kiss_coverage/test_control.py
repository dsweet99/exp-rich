"""Kiss static coverage for rich.control."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.control

def test_kiss_control_symbols_0():
    _mod = _import_rich('control')
    Control = getattr(_mod, 'Control')
    escape_control_codes = getattr(_mod, 'escape_control_codes')
    strip_control_codes = getattr(_mod, 'strip_control_codes')
    assert Control is not None
    assert escape_control_codes is not None
    assert strip_control_codes is not None
