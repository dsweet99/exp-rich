"""Kiss static coverage for rich._console_init."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._console_init

def test_kiss__console_init_symbols_0():
    _mod = _import_rich('_console_init')
    resolve_color_system = getattr(_mod, 'resolve_color_system')
    resolve_force_interactive = getattr(_mod, 'resolve_force_interactive')
    resolve_jupyter_size = getattr(_mod, 'resolve_jupyter_size')
    resolve_terminal_size = getattr(_mod, 'resolve_terminal_size')
    assert resolve_color_system is not None
    assert resolve_force_interactive is not None
    assert resolve_jupyter_size is not None
    assert resolve_terminal_size is not None
