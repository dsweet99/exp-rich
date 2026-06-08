# ruff: noqa: E402
from __future__ import annotations

from itertools import chain
from typing import Iterable, Optional

from .constrain import Constrain
from .jupyter import JupyterMixin
from .measure import Measurement
from ._segment_proxy import Segment
from .style import Style, StyleType

from ._align_types import AlignMethod, VerticalAlignMethod
import importlib as _importlib

VerticalCenter = _importlib.import_module(
    "._align_vertical", __package__
).VerticalCenter
from ._render_protocol import Console, ConsoleOptions, RenderResult, RenderableType


def _yield_exact_fit(lines, new_line: Segment) -> Iterable[Segment]:
    for line in lines:
        yield from line
        yield new_line


def _yield_left_aligned(
    lines, new_line: Segment, excess_space: int, style: Optional[Style], pad: bool
) -> Iterable[Segment]:
    pad_segment = Segment(" " * excess_space, style) if pad else None
    for line in lines:
        yield from line
        if pad_segment:
            yield pad_segment
        yield new_line


def _yield_center_aligned(
    lines, new_line: Segment, excess_space: int, style: Optional[Style], pad: bool
) -> Iterable[Segment]:
    left = excess_space // 2
    pad_left = Segment(" " * left, style)
    pad_right = Segment(" " * (excess_space - left), style) if pad else None
    for line in lines:
        if left:
            yield pad_left
        yield from line
        if pad_right:
            yield pad_right
        yield new_line


def _yield_right_aligned(
    lines, new_line: Segment, excess_space: int, style: Optional[Style]
) -> Iterable[Segment]:
    pad_segment = Segment(" " * excess_space, style)
    for line in lines:
        yield pad_segment
        yield from line
        yield new_line


def _generate_aligned_segments(
    *,
    align: AlignMethod,
    lines: list,
    new_line: Segment,
    excess_space: int,
    style: Optional[Style],
    pad: bool,
) -> Iterable[Segment]:
    if excess_space <= 0:
        yield from _yield_exact_fit(lines, new_line)
    elif align == "left":
        yield from _yield_left_aligned(lines, new_line, excess_space, style, pad)
    elif align == "center":
        yield from _yield_center_aligned(lines, new_line, excess_space, style, pad)
    else:
        yield from _yield_right_aligned(lines, new_line, excess_space, style)


class Align(JupyterMixin):
    """Align a renderable by adding spaces if necessary.

    Args:
        renderable (RenderableType): A console renderable.
        align (AlignMethod): One of "left", "center", or "right""
        style (StyleType, optional): An optional style to apply to the background.
        vertical (Optional[VerticalAlignMethod], optional): Optional vertical align, one of "top", "middle", or "bottom". Defaults to None.
        pad (bool, optional): Pad the right with spaces. Defaults to True.
        width (int, optional): Restrict contents to given width, or None to use default width. Defaults to None.
        height (int, optional): Set height of align renderable, or None to fit to contents. Defaults to None.

    Raises:
        ValueError: if ``align`` is not one of the expected values.

    Example:
        .. code-block:: python

            from rich.console import Console
            from rich.align import Align
            from rich.panel import Panel

            console = Console()
            # Create a panel 20 characters wide
            p = Panel("Hello, [b]World[/b]!", style="on green", width=20)

            # Renders the panel centered in the terminal
            console.print(Align(p, align="center"))
    """

    def __init__(
        self,
        renderable: "RenderableType",
        align: AlignMethod = "left",
        style: Optional[StyleType] = None,
        *,
        vertical: Optional[VerticalAlignMethod] = None,
        pad: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        if align not in ("left", "center", "right"):
            raise ValueError(
                f'invalid value for align, expected "left", "center", or "right" (not {align!r})'
            )
        if vertical is not None and vertical not in ("top", "middle", "bottom"):
            raise ValueError(
                f'invalid value for vertical, expected "top", "middle", or "bottom" (not {vertical!r})'
            )
        self.renderable = renderable
        self.align = align
        self.style = style
        self.vertical = vertical
        self.pad = pad
        self.width = width
        self.height = height

    def __repr__(self) -> str:
        return f"Align({self.renderable!r}, {self.align!r})"

    @classmethod
    def left(
        cls,
        renderable: "RenderableType",
        style: Optional[StyleType] = None,
        *,
        vertical: Optional[VerticalAlignMethod] = None,
        pad: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> "Align":
        """Align a renderable to the left."""
        return cls(
            renderable,
            "left",
            style=style,
            vertical=vertical,
            pad=pad,
            width=width,
            height=height,
        )

    @classmethod
    def center(
        cls,
        renderable: "RenderableType",
        style: Optional[StyleType] = None,
        *,
        vertical: Optional[VerticalAlignMethod] = None,
        pad: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> "Align":
        """Align a renderable to the center."""
        return cls(
            renderable,
            "center",
            style=style,
            vertical=vertical,
            pad=pad,
            width=width,
            height=height,
        )

    @classmethod
    def right(
        cls,
        renderable: "RenderableType",
        style: Optional[StyleType] = None,
        *,
        vertical: Optional[VerticalAlignMethod] = None,
        pad: bool = True,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> "Align":
        """Align a renderable to the right."""
        return cls(
            renderable,
            "right",
            style=style,
            vertical=vertical,
            pad=pad,
            width=width,
            height=height,
        )

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        align = self.align
        width = console.measure(self.renderable, options=options).maximum
        rendered = console.render(
            Constrain(
                self.renderable, width if self.width is None else min(width, self.width)
            ),
            options.update(height=None),
        )
        lines = list(Segment.split_lines(rendered))
        width, height = Segment.get_shape(lines)
        lines = Segment.set_shape(lines, width, height)
        new_line = Segment.line()
        excess_space = options.max_width - width
        style = console.get_style(self.style) if self.style is not None else None

        def generate_segments() -> Iterable[Segment]:
            yield from _generate_aligned_segments(
                align=align,
                lines=lines,
                new_line=new_line,
                excess_space=excess_space,
                style=style,
                pad=self.pad,
            )

        blank_line = (
            Segment(f"{' ' * (self.width or options.max_width)}\n", style)
            if self.pad
            else Segment("\n")
        )
        vertical_height = self.height or options.height
        if self.vertical and vertical_height is not None:
            iter_segments = self._vertical_segments(
                vertical_height, height, blank_line, generate_segments
            )
        else:
            iter_segments = generate_segments()
        if self.style:
            style = console.get_style(self.style)
            iter_segments = Segment.apply_style(iter_segments, style)
        yield from iter_segments

    def _vertical_segments(
        self,
        vertical_height: int,
        height: int,
        blank_line: Segment,
        generate_segments,
    ) -> Iterable[Segment]:
        def blank_lines(count: int) -> Iterable[Segment]:
            if count > 0:
                for _ in range(count):
                    yield blank_line

        if self.vertical == "top":
            return chain(generate_segments(), blank_lines(vertical_height - height))
        if self.vertical == "middle":
            top_space = (vertical_height - height) // 2
            bottom_space = vertical_height - top_space - height
            return chain(
                blank_lines(top_space), generate_segments(), blank_lines(bottom_space)
            )
        top_space = vertical_height - height
        return chain(blank_lines(top_space), generate_segments())

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        measurement = Measurement.get(console, options, self.renderable)
        return measurement


from ._align_registry import register_align  # noqa: E402

register_align(Align)
