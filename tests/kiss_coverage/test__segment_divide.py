"""Kiss static coverage for rich._segment_divide."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._segment_divide

def test_kiss__segment_divide_symbols_0():
    _mod = _import_rich('_segment_divide')
    divide_segments_at_cuts = getattr(_mod, 'divide_segments_at_cuts')
    assert divide_segments_at_cuts is not None
