from __future__ import annotations

from functools import lru_cache
from math import sqrt
from typing import Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ._types import ColorTriplet, Table



class Palette:
    """A palette of available colors."""

    def __init__(self, colors: Sequence[Tuple[int, int, int]]):
        self._colors = colors

    def __getitem__(self, number: int) -> "ColorTriplet":
        from .color_triplet import ColorTriplet

        return ColorTriplet(*self._colors[number])

    def __rich__(self) -> "Table":
        from ._pick import M_COLOR, M_STYLE, M_TABLE, M_TEXT, rich_module

        Color = rich_module(M_COLOR).Color
        Style = rich_module(M_STYLE).Style
        Text = rich_module(M_TEXT).Text
        Table = rich_module(M_TABLE).Table

        table = Table(
            "index",
            "RGB",
            "Color",
            title="Palette",
            caption=f"{len(self._colors)} colors",
            highlight=True,
            caption_justify="right",
        )
        for index, color in enumerate(self._colors):
            table.add_row(
                str(index),
                repr(color),
                Text(" " * 16, style=Style(bgcolor=Color.from_rgb(*color))),
            )
        return table

    @lru_cache(maxsize=1024)
    def match(self, color: Tuple[int, int, int]) -> int:
        """Find a color from a palette that most closely matches a given color."""
        red1, green1, blue1 = color
        _sqrt = sqrt
        get_color = self._colors.__getitem__

        def get_color_distance(index: int) -> float:
            red2, green2, blue2 = get_color(index)
            red_mean = (red1 + red2) // 2
            red = red1 - red2
            green = green1 - green2
            blue = blue1 - blue2
            return _sqrt(
                (((512 + red_mean) * red * red) >> 8)
                + 4 * green * green
                + (((767 - red_mean) * blue * blue) >> 8)
            )

        min_index = min(range(len(self._colors)), key=get_color_distance)
        return min_index
