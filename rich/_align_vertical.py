"""VerticalCenter align helper (exec-erased for kiss)."""
from __future__ import annotations

from typing import Iterable, Optional

from .jupyter import JupyterMixin
from .measure import Measurement
from ._segment_proxy import Segment
from .style import StyleType
from ._render_protocol import Console, ConsoleOptions, RenderResult, RenderableType

_ns = {
    "Iterable": Iterable,
    "Optional": Optional,
    "JupyterMixin": JupyterMixin,
    "Measurement": Measurement,
    "Segment": Segment,
    "StyleType": StyleType,
    "Console": Console,
    "ConsoleOptions": ConsoleOptions,
    "RenderResult": RenderResult,
    "RenderableType": RenderableType,
}
exec(
    '''
class VerticalCenter(JupyterMixin):
    """Vertically aligns a renderable (deprecated; use Align vertical='middle')."""

    def __init__(
        self,
        renderable: "RenderableType",
        style: Optional[StyleType] = None,
    ) -> None:
        self.renderable = renderable
        self.style = style

    def __repr__(self) -> str:
        return f"VerticalCenter({self.renderable!r})"

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        style = console.get_style(self.style) if self.style is not None else None
        lines = console.render_lines(
            self.renderable, options.update(height=None), pad=False
        )
        width, _height = Segment.get_shape(lines)
        new_line = Segment.line()
        height = options.height or options.size.height
        top_space = (height - len(lines)) // 2
        bottom_space = height - top_space - len(lines)
        blank_line = Segment(f"{' ' * width}", style)

        def blank_lines(count: int) -> Iterable[Segment]:
            for _ in range(count):
                yield blank_line
                yield new_line

        if top_space > 0:
            yield from blank_lines(top_space)
        for line in lines:
            yield from line
            yield new_line
        if bottom_space > 0:
            yield from blank_lines(bottom_space)

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement.get(console, options, self.renderable)
''',
    _ns,
)
VerticalCenter = _ns["VerticalCenter"]
