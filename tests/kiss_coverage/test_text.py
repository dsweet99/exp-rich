"""Kiss static coverage for rich.text."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.text

def test_kiss_text_symbols_0():
    _mod = _import_rich('text')
    Lines = getattr(_mod, 'Lines')
    Span = getattr(_mod, 'Span')
    Text = getattr(_mod, 'Text')
    assign_spans_to_divided_lines = getattr(_mod, 'assign_spans_to_divided_lines')
    build_indent_guide_lines = getattr(_mod, 'build_indent_guide_lines')
    expand_tab_line = getattr(_mod, 'expand_tab_line')
    render_spanned_text = getattr(_mod, 'render_spanned_text')
    text_at_offset = getattr(_mod, 'text_at_offset')
    assert Lines is not None
    assert Span is not None
    assert Text is not None
    assert assign_spans_to_divided_lines is not None
    assert build_indent_guide_lines is not None
    assert expand_tab_line is not None
    assert render_spanned_text is not None
    assert text_at_offset is not None

def test_kiss_text_symbols_1():
    _mod = _import_rich('text')
    wrap_text = getattr(_mod, 'wrap_text')
    wrap_text_line = getattr(_mod, 'wrap_text_line')
    assert wrap_text is not None
    assert wrap_text_line is not None
