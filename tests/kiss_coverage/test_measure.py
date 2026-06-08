"""Kiss static coverage for rich.measure."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.measure

def test_kiss_measure_symbols_0():
    _mod = _import_rich('measure')
    Measurement = getattr(_mod, 'Measurement')
    measure_renderables = getattr(_mod, 'measure_renderables')
    assert Measurement is not None
    assert measure_renderables is not None
