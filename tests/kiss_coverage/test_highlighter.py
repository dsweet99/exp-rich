"""Kiss static coverage for rich.highlighter."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.highlighter

def test_kiss_highlighter_symbols_0():
    _mod = _import_rich('highlighter')
    Highlighter = getattr(_mod, 'Highlighter')
    ISO8601Highlighter = getattr(_mod, 'ISO8601Highlighter')
    JSONHighlighter = getattr(_mod, 'JSONHighlighter')
    NullHighlighter = getattr(_mod, 'NullHighlighter')
    PathHighlighter = getattr(_mod, 'PathHighlighter')
    RegexHighlighter = getattr(_mod, 'RegexHighlighter')
    ReprHighlighter = getattr(_mod, 'ReprHighlighter')
    _HighlightSpan = getattr(_mod, '_HighlightSpan')
    assert Highlighter is not None
    assert ISO8601Highlighter is not None
    assert JSONHighlighter is not None
    assert NullHighlighter is not None
    assert PathHighlighter is not None
    assert RegexHighlighter is not None
    assert ReprHighlighter is not None
    assert _HighlightSpan is not None
