"""Kiss static coverage for rich.traceback."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.traceback

def test_kiss_traceback_symbols_0():
    _mod = _import_rich('traceback')
    Frame = getattr(_mod, 'Frame')
    RichTracebackStack = getattr(_mod, 'RichTracebackStack')
    Trace = getattr(_mod, 'Trace')
    Traceback = getattr(_mod, 'Traceback')
    _SyntaxError = getattr(_mod, '_SyntaxError')
    extract_traceback = getattr(_mod, 'extract_traceback')
    render_traceback_stack = getattr(_mod, 'render_traceback_stack')
    rich_traceback_install = getattr(_mod, 'rich_traceback_install')
    assert Frame is not None
    assert RichTracebackStack is not None
    assert Trace is not None
    assert Traceback is not None
    assert _SyntaxError is not None
    assert extract_traceback is not None
    assert render_traceback_stack is not None
    assert rich_traceback_install is not None

def test_kiss_traceback_symbols_1():
    _mod = _import_rich('traceback')
    traceback_example_bar = getattr(_mod, 'traceback_example_bar')
    traceback_example_foo = getattr(_mod, 'traceback_example_foo')
    assert traceback_example_bar is not None
    assert traceback_example_foo is not None
