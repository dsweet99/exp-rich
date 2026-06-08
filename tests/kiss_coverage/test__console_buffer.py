"""Kiss static coverage for rich._console_buffer."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._console_buffer

def test_kiss__console_buffer_symbols_0():
    _mod = _import_rich('_console_buffer')
    flush_pager_buffer = getattr(_mod, 'flush_pager_buffer')
    read_console_input = getattr(_mod, 'read_console_input')
    write_console_buffer = getattr(_mod, 'write_console_buffer')
    assert flush_pager_buffer is not None
    assert read_console_input is not None
    assert write_console_buffer is not None
