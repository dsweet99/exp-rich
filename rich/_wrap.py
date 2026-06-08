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


def _append_folded_word(
    break_positions: list[int],
    word: str,
    start: int,
    width: int,
    cell_offset: int,
) -> tuple[int, int]:
    """Fold an oversized word across multiple lines."""
    append = break_positions.append
    _cell_len = cell_len
    folded_word = chop_cells(word, width=width)
    for last, line in loop_last(folded_word):
        if start:
            append(start)
        if last:
            cell_offset = _cell_len(line)
        else:
            start += len(line)
    return start, cell_offset


def _handle_oversized_word(
    break_positions: list[int],
    word: str,
    start: int,
    width: int,
    word_length: int,
    fold: bool,
    cell_offset: int,
) -> tuple[int, int]:
    if fold:
        return _append_folded_word(break_positions, word, start, width, cell_offset)
    append = break_positions.append
    if start:
        append(start)
    return start, cell_len(word)


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
        if word_length > width:
            start, cell_offset = _handle_oversized_word(
                break_positions, word, start, width, word_length, fold, cell_offset
            )
        elif cell_offset and start:
            append(start)
            cell_offset = _cell_len(word)

    return break_positions

