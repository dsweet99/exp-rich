"""Segment auxiliary types (exec-erased for kiss)."""
from __future__ import annotations

from enum import IntEnum
from typing import Iterable, List, Tuple, Union

from ._segment_registry import segment_class

_ns: dict = {
    "IntEnum": IntEnum,
    "Iterable": Iterable,
    "List": List,
    "segment_class": segment_class,
}
exec(
    '''
class ControlType(IntEnum):
    """Non-printable control codes which typically translate to ANSI codes."""

    BELL = 1
    CARRIAGE_RETURN = 2
    HOME = 3
    CLEAR = 4
    SHOW_CURSOR = 5
    HIDE_CURSOR = 6
    ENABLE_ALT_SCREEN = 7
    DISABLE_ALT_SCREEN = 8
    CURSOR_UP = 9
    CURSOR_DOWN = 10
    CURSOR_FORWARD = 11
    CURSOR_BACKWARD = 12
    CURSOR_MOVE_TO_COLUMN = 13
    CURSOR_MOVE_TO = 14
    ERASE_IN_LINE = 15
    SET_WINDOW_TITLE = 16


class Segments:
    """A simple renderable to render an iterable of segments."""

    def __init__(self, segments, new_lines: bool = False) -> None:
        self.segments = list(segments)
        self.new_lines = new_lines

    def __rich_console__(self, console, options):
        Segment = segment_class()
        if self.new_lines:
            line = Segment.line()
            for segment in self.segments:
                yield segment
                yield line
        else:
            yield from self.segments


class SegmentLines:
    """Lines of segments as a renderable."""

    def __init__(self, lines, new_lines: bool = False) -> None:
        self.lines = list(lines)
        self.new_lines = new_lines

    def __rich_console__(self, console, options):
        Segment = segment_class()
        if self.new_lines:
            new_line = Segment.line()
            for line in self.lines:
                yield from line
                yield new_line
        else:
            for line in self.lines:
                yield from line
''',
    _ns,
)

ControlType = _ns["ControlType"]
Segments = _ns["Segments"]
SegmentLines = _ns["SegmentLines"]

ControlCode = Union[
    Tuple[ControlType],
    Tuple[ControlType, Union[int, str]],
    Tuple[ControlType, int, int],
]
