"""Helpers for splitting segment iterables into lines."""

from __future__ import annotations

from typing import Iterable, List, Optional, Tuple, Type

from .cells import set_cell_size


def _iter_newline_parts(segment_cls: Type, text: str, style):
    while text:
        part, new_line, text = text.partition("\n")
        if part:
            yield segment_cls(part, style), False
        if new_line:
            yield None, True


def split_segments_into_lines(segment_cls: Type, segments: Iterable) -> Iterable[List]:
    line: List = []
    append = line.append
    for segment in segments:
        if "\n" not in segment.text or segment.control:
            append(segment)
            continue
        text, style, _ = segment
        for piece, is_break in _iter_newline_parts(segment_cls, text, style):
            if is_break:
                yield line
                line = []
                append = line.append
                continue
            append(piece)
    if line:
        yield line


def split_segments_with_terminator(
    segment_cls: Type, segments: Iterable
) -> Iterable[Tuple[List, bool]]:
    line: List = []
    append = line.append
    for segment in segments:
        if "\n" not in segment.text or segment.control:
            append(segment)
            continue
        text, style, _ = segment
        for piece, is_break in _iter_newline_parts(segment_cls, text, style):
            if is_break:
                yield (line, True)
                line = []
                append = line.append
                continue
            append(piece)
    if line:
        yield (line, False)


def _crop_line_segments(
    segment_cls: Type,
    line: List,
    adjust_line_length,
    length: int,
    style,
    pad: bool,
    include_new_lines: bool,
    new_line_segment,
):
    cropped_line = adjust_line_length(line, length, style=style, pad=pad)
    if include_new_lines:
        cropped_line.append(new_line_segment)
    return cropped_line


def _split_segment_on_newlines(
    segment_cls: Type,
    segment,
    line: List,
    append,
    adjust_line_length,
    length: int,
    style,
    pad: bool,
    include_new_lines: bool,
    new_line_segment,
):
    text, segment_style, _ = segment
    while text:
        _text, new_line, text = text.partition("\n")
        if _text:
            append(segment_cls(_text, segment_style))
        if not new_line:
            continue
        yield _crop_line_segments(
            segment_cls,
            line,
            adjust_line_length,
            length,
            style,
            pad,
            include_new_lines,
            new_line_segment,
        )
        line.clear()


def split_and_crop_segment_lines(
    segment_cls: Type,
    segments: Iterable,
    length: int,
    style=None,
    pad: bool = True,
    include_new_lines: bool = True,
) -> Iterable[List]:
    """Split segments into lines and crop each to a given cell length."""
    line: List = []
    append = line.append
    adjust_line_length = segment_cls.adjust_line_length
    new_line_segment = segment_cls("\n")

    for segment in segments:
        if "\n" not in segment.text or segment.control:
            append(segment)
            continue
        yield from _split_segment_on_newlines(
            segment_cls,
            segment,
            line,
            append,
            adjust_line_length,
            length,
            style,
            pad,
            include_new_lines,
            new_line_segment,
        )
    if line:
        yield adjust_line_length(line, length, style=style, pad=pad)


def _crop_overflow_segment(segment_cls: Type, segment, line: List, length: int, line_length: int):
    text, segment_style, _ = segment
    text = set_cell_size(text, length - line_length)
    line.append(segment_cls(text, segment_style))


def adjust_segment_line_length(
    segment_cls: Type,
    line: List,
    length: int,
    style=None,
    pad: bool = True,
) -> List:
    """Crop or pad a line of segments to a given cell length."""
    line_length = sum(segment.cell_length for segment in line)
    if line_length < length:
        if pad:
            return line + [segment_cls(" " * (length - line_length), style)]
        return line[:]
    if line_length <= length:
        return line[:]

    new_line: List = []
    append = new_line.append
    line_length = 0
    for segment in line:
        segment_length = segment.cell_length
        if line_length + segment_length < length or segment.control:
            append(segment)
            line_length += segment_length
            continue
        _crop_overflow_segment(segment_cls, segment, new_line, length, line_length)
        break
    return new_line

