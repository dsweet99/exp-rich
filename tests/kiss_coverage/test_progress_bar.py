"""Kiss static coverage for rich.progress_bar."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.progress_bar

def test_kiss_progress_bar_symbols_0():
    _mod = _import_rich('progress_bar')
    ProgressBar = getattr(_mod, 'ProgressBar')
    assert ProgressBar is not None
