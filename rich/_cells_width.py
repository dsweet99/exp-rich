"""Shared cell-width helpers (extracted for kiss exec loaders)."""
from __future__ import annotations

from functools import lru_cache
from typing import Callable

from rich._unicode_data import load as load_cell_table

_SINGLE_CELL_UNICODE_RANGES: list[tuple[int, int]] = [
    (0x20, 0x7E),
    (0xA0, 0xAC),
    (0xAE, 0x002FF),
    (0x00370, 0x00482),
    (0x02500, 0x025FC),
    (0x02800, 0x028FF),
]

_SINGLE_CELLS = frozenset(
    character
    for _start, _end in _SINGLE_CELL_UNICODE_RANGES
    for character in map(chr, range(_start, _end + 1))
)

_is_single_cell_widths: Callable[[str], bool] = _SINGLE_CELLS.issuperset


@lru_cache(maxsize=4096)
def get_character_cell_size(character: str, unicode_version: str = "auto") -> int:
    """Get the cell size of a character."""
    codepoint = ord(character)
    if codepoint and codepoint < 32 or 0x07F <= codepoint < 0x0A0:
        return 0
    table = load_cell_table(unicode_version).widths

    last_entry = table[-1]
    if codepoint > last_entry[1]:
        return 1

    lower_bound = 0
    upper_bound = len(table) - 1

    while lower_bound <= upper_bound:
        index = (lower_bound + upper_bound) >> 1
        start, end, width = table[index]
        if codepoint < start:
            upper_bound = index - 1
        elif codepoint > end:
            lower_bound = index + 1
        else:
            return width
    return 1
