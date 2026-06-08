"""Kiss static coverage for rich.terminal_theme."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.terminal_theme

def test_kiss_terminal_theme_symbols_0():
    _mod = _import_rich('terminal_theme')
    TerminalTheme = getattr(_mod, 'TerminalTheme')
    assert TerminalTheme is not None
