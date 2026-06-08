"""Kiss static coverage for rich._highlight_bridge."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._highlight_bridge

def test_kiss__highlight_bridge_symbols_0():
    _mod = _import_rich('_highlight_bridge')
    align_panel_border_label = getattr(_mod, 'align_panel_border_label')
    configure = getattr(_mod, 'configure')
    configure_markup = getattr(_mod, 'configure_markup')
    configure_panel = getattr(_mod, 'configure_panel')
    copy_text = getattr(_mod, 'copy_text')
    escape_markup = getattr(_mod, 'escape_markup')
    invoke_markup_render = getattr(_mod, 'invoke_markup_render')
    is_text = getattr(_mod, 'is_text')
    assert align_panel_border_label is not None
    assert configure is not None
    assert configure_markup is not None
    assert configure_panel is not None
    assert copy_text is not None
    assert escape_markup is not None
    assert invoke_markup_render is not None
    assert is_text is not None

def test_kiss__highlight_bridge_symbols_1():
    _mod = _import_rich('_highlight_bridge')
    make_span = getattr(_mod, 'make_span')
    normalize_panel_label = getattr(_mod, 'normalize_panel_label')
    text_create = getattr(_mod, 'text_create')
    text_from_str = getattr(_mod, 'text_from_str')
    assert make_span is not None
    assert normalize_panel_label is not None
    assert text_create is not None
    assert text_from_str is not None
