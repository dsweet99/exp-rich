"""Kiss static coverage for rich._segment_lines."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._segment_lines

def test_kiss__segment_lines_symbols_0():
    _mod = _import_rich('_segment_lines')
    adjust_segment_line_length = getattr(_mod, 'adjust_segment_line_length')
    split_and_crop_segment_lines = getattr(_mod, 'split_and_crop_segment_lines')
    split_segments_into_lines = getattr(_mod, 'split_segments_into_lines')
    split_segments_with_terminator = getattr(_mod, 'split_segments_with_terminator')
    assert adjust_segment_line_length is not None
    assert split_and_crop_segment_lines is not None
    assert split_segments_into_lines is not None
    assert split_segments_with_terminator is not None
