"""Kiss static coverage for rich._pretty_common."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._pretty_common

def test_kiss__pretty_common_symbols_0():
    _mod = _import_rich('_pretty_common')
    Node = getattr(_mod, 'Node')
    _Line = getattr(_mod, '_Line')
    assert Node is not None
    assert _Line is not None
