"""Kiss static coverage for rich.pretty."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.pretty

def test_kiss_pretty_symbols_0():
    _mod = _import_rich('pretty')
    Pretty = getattr(_mod, 'Pretty')
    install = getattr(_mod, 'install')
    is_expandable = getattr(_mod, 'is_expandable')
    pprint = getattr(_mod, 'pprint')
    pretty_repr = getattr(_mod, 'pretty_repr')
    traverse = getattr(_mod, 'traverse')
    assert Pretty is not None
    assert install is not None
    assert is_expandable is not None
    assert pprint is not None
    assert pretty_repr is not None
    assert traverse is not None
