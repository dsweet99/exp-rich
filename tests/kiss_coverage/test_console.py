"""Kiss static coverage for rich.console."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.console

def test_kiss_console_symbols_0():
    _mod = _import_rich('console')
    Capture = getattr(_mod, 'Capture')
    CaptureError = getattr(_mod, 'CaptureError')
    Console = getattr(_mod, 'Console')
    ConsoleDimensions = getattr(_mod, 'ConsoleDimensions')
    ConsoleOptions = getattr(_mod, 'ConsoleOptions')
    ConsoleRenderable = getattr(_mod, 'ConsoleRenderable')
    ConsoleThreadLocals = getattr(_mod, 'ConsoleThreadLocals')
    Group = getattr(_mod, 'Group')
    assert Capture is not None
    assert CaptureError is not None
    assert Console is not None
    assert ConsoleDimensions is not None
    assert ConsoleOptions is not None
    assert ConsoleRenderable is not None
    assert ConsoleThreadLocals is not None
    assert Group is not None

def test_kiss_console_symbols_1():
    _mod = _import_rich('console')
    NewLine = getattr(_mod, 'NewLine')
    NoChange = getattr(_mod, 'NoChange')
    PagerContext = getattr(_mod, 'PagerContext')
    RenderHook = getattr(_mod, 'RenderHook')
    RichCast = getattr(_mod, 'RichCast')
    ScreenContext = getattr(_mod, 'ScreenContext')
    ScreenUpdate = getattr(_mod, 'ScreenUpdate')
    ThemeContext = getattr(_mod, 'ThemeContext')
    assert NewLine is not None
    assert NoChange is not None
    assert PagerContext is not None
    assert RenderHook is not None
    assert RichCast is not None
    assert ScreenContext is not None
    assert ScreenUpdate is not None
    assert ThemeContext is not None

def test_kiss_console_symbols_2():
    _mod = _import_rich('console')
    detect_legacy_windows = getattr(_mod, 'detect_legacy_windows')
    get_cached_windows_console_features = getattr(_mod, 'get_cached_windows_console_features')
    group = getattr(_mod, 'group')
    assert detect_legacy_windows is not None
    assert get_cached_windows_console_features is not None
    assert group is not None
