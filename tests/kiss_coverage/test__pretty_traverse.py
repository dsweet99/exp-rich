"""Kiss static coverage for rich._pretty_traverse."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._pretty_traverse

def test_kiss__pretty_traverse_symbols_0():
    _mod = _import_rich('_pretty_traverse')
    _TraverseState = getattr(_mod, '_TraverseState')
    traverse_object = getattr(_mod, 'traverse_object')
    assert _TraverseState is not None
    assert traverse_object is not None
