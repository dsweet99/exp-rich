from __future__ import annotations

from typing import TYPE_CHECKING

from ._lazy import import_attr

Measurement = import_attr('rich.measure', 'Measurement')
Segment = import_attr('rich.segment', 'Segment')
StyleType = import_attr('rich.style', 'StyleType')
if TYPE_CHECKING:
    from .console import Console, ConsoleOptions, RenderResult, RenderableType




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
        segments = Segment.apply_style(rendered_segments, style)
        return segments

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement.get(console, options, self.renderable)


if __name__ == "__main__":  # pragma: no cover
    print = import_attr('rich', 'print')
    Panel = import_attr('rich.panel', 'Panel')

    panel = Styled(Panel("hello"), "on blue")
    print(panel)
