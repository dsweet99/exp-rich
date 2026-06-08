"""Kiss static coverage for rich.theme."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.theme

def test_kiss_theme_symbols_0():
    _mod = _import_rich('theme')
    Theme = getattr(_mod, 'Theme')
    ThemeStack = getattr(_mod, 'ThemeStack')
    ThemeStackError = getattr(_mod, 'ThemeStackError')
    assert Theme is not None
    assert ThemeStack is not None
    assert ThemeStackError is not None
