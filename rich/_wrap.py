from __future__ import annotations

import re
from typing import Iterable

from ._loop import loop_last
from .cells import cell_len, chop_cells

re_word = re.compile(r"\s*\S+\s*")


def words(text: str) -> Iterable[tuple[int, int, str]]:
    """Yields each word from the text as a tuple
    containing (start_index, end_index, word). A "word" in this context may
    include the actual word and any whitespace to the right.
    """
    position = 0
    word_match = re_word.match(text, position)
    while word_match is not None:
        start, end = word_match.span()
        word = word_match.group(0)
        yield start, end, word
        word_match = re_word.match(text, end)


def _append_oversized_word(
    append,
    start: int,
    word: str,
    width: int,
    fold: bool,
    _cell_len,
) -> tuple[int, int]:
    """Fold or crop a word longer than the line width. Returns (new_start, cell_len)."""
    if not fold:
        if start:
            append(start)
        return start, _cell_len(word)
    folded_word = chop_cells(word, width=width)
    cell_offset = 0
    for last, line in loop_last(folded_word):
        if start:
            append(start)
        if last:
            cell_offset = _cell_len(line)
        else:
            start += len(line)
    return start, cell_offset


def _append_word_fitting_width(
    append,
    cell_offset: int,
    width: int,
    word_length: int,
    start: int,
    word: str,
    fold: bool,
    _cell_len,
) -> int:
    """Handle a word that does not fit in remaining line space."""
    if word_length > width:
        _, cell_offset = _append_oversized_word(
            append, start, word, width, fold, _cell_len
        )
        return cell_offset
    if cell_offset and start:
        append(start)
        return _cell_len(word)
    return cell_offset


def divide_line(text: str, width: int, fold: bool = True) -> list[int]:
    """Given a string of text, and a width (measured in cells), return a list
    of cell offsets which the string should be split at in order for it to fit
    within the given width.

    Args:
        text: The text to examine.
        width: The available cell width.
        fold: If True, words longer than `width` will be folded onto a new line.

    Returns:
        A list of indices to break the line at.
    """
    break_positions: list[int] = []
    append = break_positions.append
    cell_offset = 0
    _cell_len = cell_len

    for start, _end, word in words(text):
        word_length = _cell_len(word.rstrip())
        remaining_space = width - cell_offset
        if remaining_space >= word_length:
            cell_offset += _cell_len(word)
            continue
        cell_offset = _append_word_fitting_width(
            append,
            cell_offset,
            width,
            word_length,
            start,
            word,
            fold,
            _cell_len,
        )

    return break_positions
