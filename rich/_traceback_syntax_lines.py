"""Traceback syntax line iteration (extracted for kiss complexity)."""
from __future__ import annotations

from typing import Iterable, Tuple

from ._loop import loop_first_last


def syntax_line_span(
    first: bool,
    last: bool,
    line_no: int,
    column1: int,
    column2: int,
) -> Tuple[int, int, int]:
    """Return (line, start_column, end_column) for one line in a syntax range."""
    if first:
        return line_no, column1, -1
    if last:
        return line_no, 0, column2
    return line_no, 0, -1


def iter_syntax_lines(
    start: Tuple[int, int], end: Tuple[int, int]
) -> Iterable[Tuple[int, int, int]]:
    """Yield start and end positions per line."""
    line1, column1 = start
    line2, column2 = end

    if line1 == line2:
        yield line1, column1, column2
        return

    for first, last, line_no in loop_first_last(range(line1, line2 + 1)):
        yield syntax_line_span(first, last, line_no, column1, column2)
