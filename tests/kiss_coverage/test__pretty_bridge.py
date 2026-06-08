"""Kiss static coverage for rich._pretty_bridge."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._pretty_bridge

def test_kiss__pretty_bridge_symbols_0():
    _mod = _import_rich('_pretty_bridge')
    register_pretty_module = getattr(_mod, 'register_pretty_module')
    pretty_helpers = getattr(_mod, 'pretty_helpers')
    assert register_pretty_module is not None
    assert pretty_helpers is not None
