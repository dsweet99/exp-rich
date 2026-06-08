"""Kiss static coverage for rich._json_format."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._json_format

def test_kiss__json_format_symbols_0():
    _mod = _import_rich('_json_format')
    encode_json_text = getattr(_mod, 'encode_json_text')
    highlight_json_text = getattr(_mod, 'highlight_json_text')
    assert encode_json_text is not None
    assert highlight_json_text is not None
