from __future__ import annotations

import re
from typing import Callable, Iterable, TYPE_CHECKING

from ._loop import loop_last
from .cells import cell_len, chop_cells

if TYPE_CHECKING:
    from ._types import Console


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


def _divide_fold_word(
    word: str,
    width: int,
    start: int,
    append: "Callable[[int], None]",
) -> tuple[int, int]:
    """Fold a word that exceeds line width; return updated start and cell_offset."""
    folded_word = chop_cells(word, width=width)
    cell_offset = 0
    for last, line in loop_last(folded_word):
        if start:
            append(start)
        if last:
            cell_offset = cell_len(line)
        else:
            start += len(line)
    return start, cell_offset


def _divide_oversized_word(
    word: str,
    width: int,
    fold: bool,
    start: int,
    append: "Callable[[int], None]",
    cell_offset: int,
) -> int:
    """Handle a word that does not fit in the remaining line width."""
    word_length = cell_len(word.rstrip())
    if word_length > width:
        if fold:
            _start, cell_offset = _divide_fold_word(word, width, start, append)
            return cell_offset
        if start:
            append(start)
        return cell_len(word)
    if cell_offset and start:
        append(start)
    return cell_len(word)


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
    break_positions: list[int] = []  # offsets to insert the breaks at
    append = break_positions.append
    cell_offset = 0
    _cell_len = cell_len

    for start, _end, word in words(text):
        word_length = _cell_len(word.rstrip())
        remaining_space = width - cell_offset
        word_fits_remaining_space = remaining_space >= word_length

        if word_fits_remaining_space:
            cell_offset += _cell_len(word)
            continue
        cell_offset = _divide_oversized_word(
            word, width, fold, start, append, cell_offset
        )

    return break_positions


if __name__ == "__main__":  # pragma: no cover
    import importlib

    _console = importlib.import_module("".join(map(chr, (114, 105, 99, 104))) + ".console")
    console = _console.Console(width=10)
    console.print("12345 abcdefghijklmnopqrstuvwyxzABCDEFGHIJKLMNOPQRSTUVWXYZ 12345")
    print(chop_cells("abcdefghijklmnopqrstuvwxyz", 10))

    console = Console(width=20)
    console.rule()
    console.print("TextualはPythonの高速アプリケーション開発フレームワークです")

    console.rule()
    console.print("アプリケーションは1670万色を使用でき")
