"""Kiss static coverage for rich._test_card."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._test_card

def test_kiss__test_card_symbols_0():
    _mod = _import_rich('_test_card')
    ColorBox = getattr(_mod, 'ColorBox')
    make_test_card = getattr(_mod, 'make_test_card')
    assert ColorBox is not None
    assert make_test_card is not None
