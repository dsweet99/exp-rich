"""Kiss static coverage for rich.__main__."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.__main__

def test_kiss___main___symbols_0():
    _mod = _import_rich('__main__')
    ColorBox = getattr(_mod, 'ColorBox')
    make_test_card = getattr(_mod, 'make_test_card')
    assert ColorBox is not None
    assert make_test_card is not None
