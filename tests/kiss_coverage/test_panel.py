"""Kiss static coverage for rich.panel."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.panel

def test_kiss_panel_symbols_0():
    _mod = _import_rich('panel')
    Panel = getattr(_mod, 'Panel')
    assert Panel is not None
