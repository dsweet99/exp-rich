from __future__ import annotations

from typing import TYPE_CHECKING
from .measure import Measurement
from ._pick import M_SEGMENT, rich_module
from .style import StyleType

if TYPE_CHECKING:
    from ._types import Console, ConsoleOptions, RenderResult, RenderableType



def _Segment():
    return rich_module(M_SEGMENT).Segment

class Styled:
    """Apply a style to a renderable.

    Args:
        renderable (RenderableType): Any renderable.
        style (StyleType): A style to apply across the entire renderable.
    """

    def __init__(self, renderable: "RenderableType", style: "StyleType") -> None:
        self.renderable = renderable
        self.style = style

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        style = console.get_style(self.style)
        rendered_segments = console.render(self.renderable, options)
        segments = _Segment().apply_style(rendered_segments, style)
        return segments

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement.get(console, options, self.renderable)

if __name__ == "__main__":  # pragma: no cover
    import importlib

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    Panel = importlib.import_module(_pkg + ".panel").Panel
    print_fn = importlib.import_module(_pkg).print
    panel = Styled(Panel("hello"), "on blue")
    print_fn(panel)