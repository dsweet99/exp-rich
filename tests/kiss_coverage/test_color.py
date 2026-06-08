"""Kiss static coverage for rich.color."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.color

def test_kiss_color_symbols_0():
    _mod = _import_rich('color')
    Color = getattr(_mod, 'Color')
    ColorParseError = getattr(_mod, 'ColorParseError')
    ColorSystem = getattr(_mod, 'ColorSystem')
    ColorType = getattr(_mod, 'ColorType')
    Style = getattr(_mod, 'Style')
    StyleStack = getattr(_mod, 'StyleStack')
    _Bit = getattr(_mod, '_Bit')
    blend_rgb = getattr(_mod, 'blend_rgb')
    assert Color is not None
    assert ColorParseError is not None
    assert ColorSystem is not None
    assert ColorType is not None
    assert Style is not None
    assert StyleStack is not None
    assert _Bit is not None
    assert blend_rgb is not None

def test_kiss_color_symbols_1():
    _mod = _import_rich('color')
    parse_rgb_hex = getattr(_mod, 'parse_rgb_hex')
    assert parse_rgb_hex is not None
