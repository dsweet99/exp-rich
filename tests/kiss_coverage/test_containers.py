"""Kiss static coverage for rich.containers."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.containers

def test_kiss_containers_symbols_0():
    _mod = _import_rich('containers')
    Renderables = getattr(_mod, 'Renderables')
    assert Renderables is not None
