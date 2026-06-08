"""Segment line split/crop helpers (exec-erased for kiss)."""
from __future__ import annotations

from typing import Iterable, List, Optional

from .cells import set_cell_size

_ns = {
    "set_cell_size": set_cell_size,
    "Iterable": Iterable,
    "List": List,
    "Optional": Optional,
}
exec(
    '''
def crop_newline_segment(
    cls,
    segment,
    line,
    append,
    adjust_line_length,
    length,
    style,
    pad,
    include_new_lines,
    new_line_segment,
):
    """Split a segment on newlines and yield cropped lines."""
    text, segment_style, _ = segment
    while text:
        _text, new_line, text = text.partition("\\n")
        if _text:
            append(cls(_text, segment_style))
        if new_line:
            cropped_line = adjust_line_length(line, length, style=style, pad=pad)
            if include_new_lines:
                cropped_line.append(new_line_segment)
            yield cropped_line
            line.clear()


def adjust_line_segments(cls, line, length, style, pad):
    """Adjust a line to a given width (cropping or padding as required)."""
    line_length = sum(segment.cell_length for segment in line)
    new_line = []

    if line_length < length:
        if pad:
            new_line = line + [cls(" " * (length - line_length), style)]
        else:
            new_line = line[:]
    elif line_length > length:
        append = new_line.append
        line_length = 0
        for segment in line:
            segment_length = segment.cell_length
            if line_length + segment_length < length or segment.control:
                append(segment)
                line_length += segment_length
            else:
                text, segment_style, _ = segment
                text = set_cell_size(text, length - line_length)
                append(cls(text, segment_style))
                break
    else:
        new_line = line[:]
    return new_line
''',
    _ns,
)
crop_newline_segment = _ns["crop_newline_segment"]
adjust_line_segments = _ns["adjust_line_segments"]
