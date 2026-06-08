from __future__ import annotations

from typing import List, Optional, Tuple, Union, TYPE_CHECKING

from ._jupyter_mixin import JupyterMixin
from ._padding_dims import PaddingDimensions, unpack_padding
from ._pick import M_SEGMENT, rich_module
from .style import Style

if TYPE_CHECKING:
    from ._types import Console, ConsoleOptions, Measurement, RenderResult, RenderableType, Segment



def _Segment():
    return rich_module(M_SEGMENT).Segment


def _yield_padded_lines(
    lines: List[List["Segment"]],
    *,
    left: Optional["Segment"],
    right: List["Segment"],
    top: int,
    bottom: int,
    width: int,
    style: Style,
    blank_line: Optional[List["Segment"]],
) -> "RenderResult":
    """Yield padded render output."""
    Segment = _Segment()
    if top:
        blank_line = blank_line or [Segment(f'{" " * width}\n', style)]
        yield from blank_line * top
    if left:
        for line in lines:
            yield left
            yield from line
            yield from right
    else:
        for line in lines:
            yield from line
            yield from right
    if bottom:
        blank_line = blank_line or [Segment(f'{" " * width}\n', style)]
        yield from blank_line * bottom


class Padding(JupyterMixin):
    """Draw space around content.

    Example:
        >>> print(Padding("Hello", (2, 4), style="on blue"))

    Args:
        renderable (RenderableType): String or other renderable.
        pad (Union[int, Tuple[int]]): Padding for top, right, bottom, and left borders.
            May be specified with 1, 2, or 4 integers (CSS style).
        style (Union[str, Style], optional): Style for padding characters. Defaults to "none".
        expand (bool, optional): Expand padding to fit available width. Defaults to True.
    """

    def __init__(
        self,
        renderable: "RenderableType",
        pad: "PaddingDimensions" = (0, 0, 0, 0),
        *,
        style: Union[str, Style] = "none",
        expand: bool = True,
    ):
        self.renderable = renderable
        self.top, self.right, self.bottom, self.left = self.unpack(pad)
        self.style = style
        self.expand = expand

    @classmethod
    def indent(cls, renderable: "RenderableType", level: int) -> "Padding":
        """Make padding instance to render an indent.

        Args:
            renderable (RenderableType): String or other renderable.
            level (int): Number of characters to indent.

        Returns:
            Padding: A Padding instance.
        """

        return Padding(renderable, pad=(0, 0, 0, level), expand=False)

    @staticmethod
    def unpack(pad: "PaddingDimensions") -> Tuple[int, int, int, int]:
        """Unpack padding specified in CSS style."""
        return unpack_padding(pad)

    def __repr__(self) -> str:
        return f"Padding({self.renderable!r}, ({self.top},{self.right},{self.bottom},{self.left}))"

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        from .measure import Measurement

        style = console.get_style(self.style)
        if self.expand:
            width = options.max_width
        else:
            width = min(
                Measurement.get(console, options, self.renderable).maximum
                + self.left
                + self.right,
                options.max_width,
            )
        render_options = options.update_width(width - self.left - self.right)
        if render_options.height is not None:
            render_options = render_options.update_height(
                height=render_options.height - self.top - self.bottom
            )
        lines = console.render_lines(
            self.renderable, render_options, style=style, pad=True
        )
        Segment = _Segment()
        left = Segment(" " * self.left, style) if self.left else None
        right = (
            [Segment(f'{" " * self.right}', style), Segment.line()]
            if self.right
            else [Segment.line()]
        )
        yield from _yield_padded_lines(
            lines,
            left=left,
            right=right,
            top=self.top,
            bottom=self.bottom,
            width=width,
            style=style,
            blank_line=None,
        )

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        from .measure import Measurement

        max_width = options.max_width
        extra_width = self.left + self.right
        if max_width - extra_width < 1:
            return Measurement(max_width, max_width)
        measure_min, measure_max = Measurement.get(console, options, self.renderable)
        measurement = Measurement(measure_min + extra_width, measure_max + extra_width)
        measurement = measurement.with_maximum(max_width)
        return measurement


if __name__ == "__main__":  #  pragma: no cover
    from . import print

    print(Padding("Hello, World", (2, 4), style="on blue"))
