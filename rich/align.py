from __future__ import annotations

from itertools import chain
from typing import Callable, Iterable, List, Optional, TYPE_CHECKING

from ._align_types import AlignMethod, VerticalAlignMethod
from .constrain import Constrain
from ._jupyter_mixin import JupyterMixin
from .measure import Measurement
from ._pick import M_SEGMENT, rich_module
from .style import StyleType

if TYPE_CHECKING:
    from ._types import ConsoleOptions, RenderResult, RenderableType, Segment



def _Segment():
    return rich_module(M_SEGMENT).Segment

def _align_generate_exact(
    lines: List[List["Segment"]], new_line: "Segment"
) -> Iterable["Segment"]:
    for line in lines:
        yield from line
        yield new_line

def _align_generate_left(
    lines: List[List["Segment"]],
    excess_space: int,
    style: Optional[StyleType],
    pad: bool,
    new_line: "Segment",
) -> Iterable["Segment"]:
    Segment = _Segment()
    pad_segment = Segment(" " * excess_space, style) if pad else None
    for line in lines:
        yield from line
        if pad_segment:
            yield pad_segment
        yield new_line

def _align_generate_center(
    lines: List[List[Segment]],
    excess_space: int,
    style: Optional[StyleType],
    pad: bool,
    new_line: Segment,
) -> Iterable[Segment]:
    Segment = _Segment()
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

def _align_generate_right(
    lines: List[List[Segment]],
    excess_space: int,
    style: Optional[StyleType],
    new_line: Segment,
) -> Iterable[Segment]:
    Segment = _Segment()
    pad_segment = Segment(" " * excess_space, style)
    for line in lines:
        yield pad_segment
        yield from line
        yield new_line

def _align_generate_segments(
    align: AlignMethod,
    lines: List[List[Segment]],
    excess_space: int,
    style: Optional[StyleType],
    pad: bool,
    new_line: Segment,
) -> Iterable[Segment]:
    if excess_space <= 0:
        yield from _align_generate_exact(lines, new_line)
        return
    if align == "left":
        yield from _align_generate_left(lines, excess_space, style, pad, new_line)
        return
    if align == "center":
        yield from _align_generate_center(lines, excess_space, style, pad, new_line)
        return
    yield from _align_generate_right(lines, excess_space, style, new_line)

def _align_vertical_segments(
    vertical: VerticalAlignMethod,
    vertical_height: int,
    height: int,
    generate_segments: Iterable[Segment],
    blank_lines: "Callable[[int], Iterable[Segment]]",
) -> Iterable[Segment]:
    if vertical == "top":
        yield from chain(generate_segments, blank_lines(vertical_height - height))
        return
    if vertical == "middle":
        top_space = (vertical_height - height) // 2
        bottom_space = vertical_height - top_space - height
        yield from chain(
            blank_lines(top_space),
            generate_segments,
            blank_lines(bottom_space),
        )
        return
    yield from chain(blank_lines(vertical_height - height), generate_segments)

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
        Center a renderable with ``Align(renderable, align="center")``.
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
        Segment = _Segment()
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

        generate_segments = _align_generate_segments(
            align, lines, excess_space, style, self.pad, new_line
        )

        blank_line = (
            Segment(f"{' ' * (self.width or options.max_width)}\n", style)
            if self.pad
            else Segment("\n")
        )

        def blank_lines(count: int) -> Iterable[Segment]:
            if count > 0:
                for _ in range(count):
                    yield blank_line

        vertical_height = self.height or options.height
        if self.vertical and vertical_height is not None:
            iter_segments = _align_vertical_segments(
                self.vertical,
                vertical_height,
                height,
                generate_segments,
                blank_lines,
            )
        else:
            iter_segments = generate_segments
        if self.style:
            style = console.get_style(self.style)
            iter_segments = Segment.apply_style(iter_segments, style)
        yield from iter_segments

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        measurement = Measurement.get(console, options, self.renderable)
        return measurement

def _vertical_center_init(
    self,
    renderable: "RenderableType",
    style: Optional[StyleType] = None,
) -> None:
    self.renderable = renderable
    self.style = style

def _vertical_center_repr(self) -> str:
    return f"VerticalCenter({self.renderable!r})"

def _vertical_center_rich_console(
    self, console: "Console", options: "ConsoleOptions"
) -> "RenderResult":
    Segment = _Segment()
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

def _vertical_center_rich_measure(
    self, console: "Console", options: "ConsoleOptions"
) -> Measurement:
    return Measurement.get(console, options, self.renderable)

VerticalCenter = type(
    "VerticalCenter",
    (JupyterMixin,),
    {
        "__doc__": (
            "Vertically aligns a renderable.\n\n"
            "Warn:\n"
            "    This class is deprecated and may be removed in a future version. Use Align class with\n"
            '    `vertical="middle"`.'
        ),
        "__init__": _vertical_center_init,
        "__repr__": _vertical_center_repr,
        "__rich_console__": _vertical_center_rich_console,
        "__rich_measure__": _vertical_center_rich_measure,
    },
)

if __name__ == "__main__":  # pragma: no cover
    import importlib

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    Console = importlib.import_module(_pkg + ".console").Console
    Group = importlib.import_module(_pkg + ".console").Group
    ReprHighlighter = importlib.import_module(_pkg + ".highlighter").ReprHighlighter
    Panel = importlib.import_module(_pkg + ".panel").Panel

    highlighter = ReprHighlighter()
    console = Console()

    panel = Panel(
        Group(
            Align.left(highlighter("align='left'")),
            Align.center(highlighter("align='center'")),
            Align.right(highlighter("align='right'")),
        ),
        width=60,
        style="on dark_blue",
        title="Align",
    )

    console.print(
        Align.center(panel, vertical="middle", style="on red", height=console.height)
    )