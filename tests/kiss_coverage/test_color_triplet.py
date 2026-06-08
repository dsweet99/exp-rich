"""Kiss static coverage for rich.color_triplet."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.color_triplet

def test_kiss_color_triplet_symbols_0():
    _mod = _import_rich('color_triplet')
    ColorTriplet = getattr(_mod, 'ColorTriplet')
    assert ColorTriplet is not None
