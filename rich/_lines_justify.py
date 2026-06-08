"""Lines justify helpers (extracted for kiss)."""
from __future__ import annotations

from itertools import zip_longest
from typing import TYPE_CHECKING, Iterable, List

from .cells import cell_len

if TYPE_CHECKING:
    from ._render_protocol import Console, Text
    from ._align_types import OverflowMethod


def justify_left(lines: Iterable["Text"], width: int, overflow: "OverflowMethod") -> None:
    for line in lines:
        line.truncate(width, overflow=overflow, pad=True)


def justify_center(
    lines: Iterable["Text"], width: int, overflow: "OverflowMethod"
) -> None:
    for line in lines:
        line.rstrip()
        line.truncate(width, overflow=overflow)
        line.pad_left((width - cell_len(line.plain)) // 2)
        line.pad_right(width - cell_len(line.plain))


def justify_right(
    lines: Iterable["Text"], width: int, overflow: "OverflowMethod"
) -> None:
    for line in lines:
        line.rstrip()
        line.truncate(width, overflow=overflow)
        line.pad_left(width - cell_len(line.plain))


def justify_full(
    lines: List["Text"],
    console: "Console",
    width: int,
    Text: type,
) -> None:
    for line_index, line in enumerate(lines):
        if line_index == len(lines) - 1:
            break
        words = line.split(" ")
        words_size = sum(cell_len(word.plain) for word in words)
        num_spaces = len(words) - 1
        spaces = [1 for _ in range(num_spaces)]
        index = 0
        if spaces:
            while words_size + num_spaces < width:
                spaces[len(spaces) - index - 1] += 1
                num_spaces += 1
                index = (index + 1) % len(spaces)
        tokens: List["Text"] = []
        for index, (word, next_word) in enumerate(zip_longest(words, words[1:])):
            tokens.append(word)
            if index < len(spaces):
                style = word.get_style_at_offset(console, -1)
                next_style = next_word.get_style_at_offset(console, 0)
                space_style = style if style == next_style else line.style
                tokens.append(Text(" " * spaces[index], style=space_style))
        lines[line_index] = Text("").join(tokens)
