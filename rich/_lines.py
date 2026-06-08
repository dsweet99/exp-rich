from __future__ import annotations

from itertools import zip_longest
from typing import Iterable, Iterator, List, Union, overload, TYPE_CHECKING

from ._pick import M_TEXT, rich_module
from .cells import cell_len

if TYPE_CHECKING:
    from ._types import Console, ConsoleOptions, JustifyMethod, OverflowMethod, RenderResult, Text



def _lines_justify_left(
    lines: List[Text], width: int, overflow: OverflowMethod
) -> None:
    for line in lines:
        line.truncate(width, overflow=overflow, pad=True)


def _lines_justify_center(
    lines: List[Text], width: int, overflow: OverflowMethod
) -> None:
    for line in lines:
        line.rstrip()
        line.truncate(width, overflow=overflow)
        line.pad_left((width - cell_len(line.plain)) // 2)
        line.pad_right(width - cell_len(line.plain))


def _lines_justify_right(
    lines: List[Text], width: int, overflow: OverflowMethod
) -> None:
    for line in lines:
        line.rstrip()
        line.truncate(width, overflow=overflow)
        line.pad_left(width - cell_len(line.plain))


def _lines_justify_full(lines: List[Text], console: Console, width: int) -> None:
    Text = rich_module(M_TEXT).Text

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
        tokens: List[Text] = []
        for index, (word, next_word) in enumerate(zip_longest(words, words[1:])):
            tokens.append(word)
            if index < len(spaces):
                style = word.get_style_at_offset(console, -1)
                next_style = next_word.get_style_at_offset(console, 0)
                space_style = style if style == next_style else line.style
                tokens.append(Text(" " * spaces[index], style=space_style))
        lines[line_index] = Text("").join(tokens)


class Lines:
    """A list subclass which can render to the console."""

    def __init__(self, lines: Iterable[Text] = ()) -> None:
        self._lines: List[Text] = list(lines)

    def __repr__(self) -> str:
        return f"Lines({self._lines!r})"

    def __iter__(self) -> Iterator[Text]:
        return iter(self._lines)

    @overload
    def __getitem__(self, index: int) -> Text:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[Text]:
        ...

    def __getitem__(self, index: Union[slice, int]) -> Union[Text, List[Text]]:
        return self._lines[index]

    def __setitem__(self, index: int, value: Text) -> Lines:
        self._lines[index] = value
        return self

    def __len__(self) -> int:
        return self._lines.__len__()

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Console render method to insert line-breaks."""
        yield from self._lines

    def append(self, line: Text) -> None:
        self._lines.append(line)

    def extend(self, lines: Iterable[Text]) -> None:
        self._lines.extend(lines)

    def pop(self, index: int = -1) -> Text:
        return self._lines.pop(index)

    def justify(
        self,
        console: Console,
        width: int,
        justify: JustifyMethod = "left",
        overflow: OverflowMethod = "fold",
    ) -> None:
        """Justify and overflow text to a given width."""
        if justify == "left":
            _lines_justify_left(self._lines, width, overflow)
        elif justify == "center":
            _lines_justify_center(self._lines, width, overflow)
        elif justify == "right":
            _lines_justify_right(self._lines, width, overflow)
        elif justify == "full":
            _lines_justify_full(self._lines, console, width)
