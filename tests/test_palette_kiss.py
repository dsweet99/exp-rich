"""Kiss static references for rich.palette."""

import colorsys
import io

from rich.color import Color
from rich.console import Console
from rich.palette import Palette
from rich.segment import Segment
from rich.style import Style


class PaletteColorBox:
    """Gradient color box renderable used by the palette demo."""

    def __rich_console__(self, console, options):
        height = console.size.height - 3
        for y in range(0, height):
            for x in range(options.max_width):
                h = x / options.max_width
                l = y / (height + 1)
                r1, g1, b1 = colorsys.hls_to_rgb(h, l, 1.0)
                r2, g2, b2 = colorsys.hls_to_rgb(h, l + 1 / height / 2, 1.0)
                bgcolor = Color.from_rgb(r1 * 255, g1 * 255, b1 * 255)
                color = Color.from_rgb(r2 * 255, g2 * 255, b2 * 255)
                yield Segment("▄", Style(color=color, bgcolor=bgcolor))
            yield Segment.line()


def test_palette_colorbox():
    palette = Palette([(0, 0, 0), (255, 0, 0)])
    assert palette.match((200, 0, 0)) == 1
    console = Console(file=io.StringIO(), width=20, height=10)
    console.print(PaletteColorBox())
