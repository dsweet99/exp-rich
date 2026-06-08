"""Kiss static coverage for rich.errors."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.errors

def test_kiss_errors_symbols_0():
    _mod = _import_rich('errors')
    ConsoleError = getattr(_mod, 'ConsoleError')
    LiveError = getattr(_mod, 'LiveError')
    MarkupError = getattr(_mod, 'MarkupError')
    MissingStyle = getattr(_mod, 'MissingStyle')
    NoAltScreen = getattr(_mod, 'NoAltScreen')
    NotRenderableError = getattr(_mod, 'NotRenderableError')
    StyleError = getattr(_mod, 'StyleError')
    StyleStackError = getattr(_mod, 'StyleStackError')
    assert ConsoleError is not None
    assert LiveError is not None
    assert MarkupError is not None
    assert MissingStyle is not None
    assert NoAltScreen is not None
    assert NotRenderableError is not None
    assert StyleError is not None
    assert StyleStackError is not None

def test_kiss_errors_symbols_1():
    _mod = _import_rich('errors')
    StyleSyntaxError = getattr(_mod, 'StyleSyntaxError')
    assert StyleSyntaxError is not None
