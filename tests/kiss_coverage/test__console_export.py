"""Kiss static coverage for rich._console_export."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._console_export

def test_kiss__console_export_symbols_0():
    _mod = _import_rich('_console_export')
    export_html_buffer = getattr(_mod, 'export_html_buffer')
    export_svg_buffer = getattr(_mod, 'export_svg_buffer')
    assert export_html_buffer is not None
    assert export_svg_buffer is not None
