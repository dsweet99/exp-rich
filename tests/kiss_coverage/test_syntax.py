"""Kiss static coverage for rich.syntax."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.syntax

def test_kiss_syntax_symbols_0():
    _mod = _import_rich('syntax')
    ANSISyntaxTheme = getattr(_mod, 'ANSISyntaxTheme')
    PaddingProperty = getattr(_mod, 'PaddingProperty')
    PygmentsSyntaxTheme = getattr(_mod, 'PygmentsSyntaxTheme')
    Syntax = getattr(_mod, 'Syntax')
    SyntaxTheme = getattr(_mod, 'SyntaxTheme')
    _SyntaxHighlightRange = getattr(_mod, '_SyntaxHighlightRange')
    assert ANSISyntaxTheme is not None
    assert PaddingProperty is not None
    assert PygmentsSyntaxTheme is not None
    assert Syntax is not None
    assert SyntaxTheme is not None
    assert _SyntaxHighlightRange is not None
