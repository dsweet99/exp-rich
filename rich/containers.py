from __future__ import annotations

import importlib as _importlib
from typing import (
    Iterable,
    Iterator,
    List,
    TypeVar,
    Union,
    overload,
)

from ._align_types import JustifyMethod, OverflowMethod
from ._containers_renderables import Renderables  # noqa: F401
from ._render_factory import register_renderables
from ._render_protocol import Console, ConsoleOptions, RenderResult, Text

T = TypeVar("T")


class Lines:
    """A list subclass which can render to the console."""

    def __init__(self, lines: Iterable["Text"] = ()) -> None:
        self._lines: List["Text"] = list(lines)

    def __repr__(self) -> str:
        return f"Lines({self._lines!r})"

    def __iter__(self) -> Iterator["Text"]:
        return iter(self._lines)

    @overload
    def __getitem__(self, index: int) -> "Text":
        ...

    @overload
    def __getitem__(self, index: slice) -> List["Text"]:
        ...

    def __getitem__(self, index: Union[slice, int]) -> Union["Text", List["Text"]]:
        return self._lines[index]

    def __setitem__(self, index: int, value: "Text") -> "Lines":
        self._lines[index] = value
        return self

    def __len__(self) -> int:
        return self._lines.__len__()

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        """Console render method to insert line-breaks."""
        yield from self._lines

    def append(self, line: "Text") -> None:
        self._lines.append(line)

    def extend(self, lines: Iterable["Text"]) -> None:
        self._lines.extend(lines)

    def pop(self, index: int = -1) -> "Text":
        return self._lines.pop(index)

    def justify(
        self,
        console: "Console",
        width: int,
        justify: "JustifyMethod" = "left",
        overflow: "OverflowMethod" = "fold",
    ) -> None:
        """Justify and overflow text to a given width.

        Args:
            console (Console): Console instance.
            width (int): Number of cells available per line.
            justify (str, optional): Default justify method for text: "left", "center", "full" or "right". Defaults to "left".
            overflow (str, optional): Default overflow for text: "crop", "fold", or "ellipsis". Defaults to "fold".

        """
        Text = _importlib.import_module(".text", __package__).Text

        if justify == "left":
            from ._lines_justify import justify_left

            justify_left(self._lines, width, overflow)
        elif justify == "center":
            from ._lines_justify import justify_center

            justify_center(self._lines, width, overflow)
        elif justify == "right":
            from ._lines_justify import justify_right

            justify_right(self._lines, width, overflow)
        elif justify == "full":
            from ._lines_justify import justify_full

            justify_full(self._lines, console, width, Text)


register_renderables(Renderables)
