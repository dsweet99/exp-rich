"""Kiss static coverage for rich.segment."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.segment

def test_kiss_segment_symbols_0():
    _mod = _import_rich('segment')
    ControlType = getattr(_mod, 'ControlType')
    Segment = getattr(_mod, 'Segment')
    SegmentLines = getattr(_mod, 'SegmentLines')
    Segments = getattr(_mod, 'Segments')
    assert ControlType is not None
    assert Segment is not None
    assert SegmentLines is not None
    assert Segments is not None
