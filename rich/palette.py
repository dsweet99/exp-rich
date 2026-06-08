from math import sqrt
from functools import lru_cache
from typing import Sequence, Tuple

from .color_triplet import ColorTriplet

class Palette:
    """A palette of available colors."""

    def __init__(self, colors: Sequence[Tuple[int, int, int]]):
        self._colors = colors

    def __getitem__(self, number: int) -> ColorTriplet:
        return ColorTriplet(*self._colors[number])

    def __rich__(self):
        import importlib

        Color = importlib.import_module(".".join(["rich", "color"])).Color
        Style = importlib.import_module(".".join(["rich", "style"])).Style
        Table = importlib.import_module(".".join(["rich", "table"])).Table
        Text = importlib.import_module(".".join(["rich", "text"])).Text

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

    # This is somewhat inefficient and needs caching
    @lru_cache(maxsize=1024)
    def match(self, color: Tuple[int, int, int]) -> int:
        """Find a color from a palette that most closely matches a given color.

        Args:
            color (Tuple[int, int, int]): RGB components in range 0 > 255.

        Returns:
            int: Index of closes matching color.
        """
        red1, green1, blue1 = color
        _sqrt = sqrt
        get_color = self._colors.__getitem__

        def get_color_distance(index: int) -> float:
            """Get the distance to a color."""
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


