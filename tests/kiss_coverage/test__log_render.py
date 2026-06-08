"""Kiss static coverage for rich._log_render."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._log_render

def test_kiss__log_render_symbols_0():
    _mod = _import_rich('_log_render')
    LogRender = getattr(_mod, 'LogRender')
    assert LogRender is not None
