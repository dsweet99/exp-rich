"""Kiss static coverage for rich._jupyter_mixin."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._jupyter_mixin

def test_kiss__jupyter_mixin_symbols_0():
    _mod = _import_rich('_jupyter_mixin')
    JupyterMixin = getattr(_mod, 'JupyterMixin')
    assert JupyterMixin is not None
