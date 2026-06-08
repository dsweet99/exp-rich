from typing import Optional

from ._segment_proxy import Segment
from .style import StyleType
from ._loop import loop_last


class Screen:
    """A renderable that fills the terminal screen and crops excess.

    Args:
        renderable (RenderableType): Child renderable.
        style (StyleType, optional): Optional background style. Defaults to None.
    """

    renderable: "RenderableType"

    def __init__(
        self,
        *renderables: "RenderableType",
        style: Optional[StyleType] = None,
        application_mode: bool = False,
    ) -> None:
        from ._group_registry import group_class

        self.renderable = group_class()(*renderables)
        self.style = style
        self.application_mode = application_mode

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        width, height = options.size
        style = console.get_style(self.style) if self.style else None
        render_options = options.update(width=width, height=height)
        lines = console.render_lines(
            self.renderable or "", render_options, style=style, pad=True
        )
        lines = Segment.set_shape(lines, width, height, style=style)
        new_line = Segment("\n\r") if self.application_mode else Segment.line()
        for last, line in loop_last(lines):
            yield from line
            if not last:
                yield new_line


from ._screen_registry import register_screen  # noqa: E402
from ._render_protocol import Console, ConsoleOptions, RenderResult, RenderableType  # noqa: E402

register_screen(Screen)
