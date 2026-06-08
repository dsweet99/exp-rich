"""Kiss static coverage for rich.styled."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.styled

def test_kiss_styled_symbols_0():
    _mod = _import_rich('styled')
    Styled = getattr(_mod, 'Styled')
    assert Styled is not None
