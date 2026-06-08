"""Syntax._apply_stylized_ranges helpers (extracted for kiss)."""
from __future__ import annotations

import re
from typing import Optional, Sequence

from .text import Text


def apply_stylized_ranges(text: Text, stylized_ranges: Sequence[object]) -> None:
    """Apply stylized ranges to a text instance."""
    code = text.plain
    newlines_offsets = [
        0,
        *[match.start() + 1 for match in re.finditer("\n", code, flags=re.MULTILINE)],
        len(code) + 1,
    ]

    for stylized_range in stylized_ranges:
        _apply_one_stylized_range(text, stylized_range, newlines_offsets)


def _apply_one_stylized_range(
    text: Text, stylized_range: object, newlines_offsets: Sequence[int]
) -> None:
    start = get_code_index_for_syntax_position(
        newlines_offsets, stylized_range.start
    )
    end = get_code_index_for_syntax_position(newlines_offsets, stylized_range.end)
    if start is None or end is None:
        return
    if stylized_range.style_before:
        text.stylize_before(stylized_range.style, start, end)
    else:
        text.stylize(stylized_range.style, start, end)


def get_code_index_for_syntax_position(
    newlines_offsets: Sequence[int], position: object
) -> Optional[int]:
    """Return the code-string index for a syntax position."""
    lines_count = len(newlines_offsets)

    line_number, column_index = position
    if line_number > lines_count or len(newlines_offsets) < (line_number + 1):
        return None
    line_index = line_number - 1
    line_length = newlines_offsets[line_index + 1] - newlines_offsets[line_index] - 1
    column_index = min(line_length, column_index)
    return newlines_offsets[line_index] + column_index
