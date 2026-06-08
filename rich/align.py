from itertools import chain
from typing import TYPE_CHECKING, Iterable, Optional, Literal
from .constrain import Constrain
from .measure import Measurement
from ._jupyter_mixin import JupyterMixin
from .segment import Segment
from .style import StyleType
AlignMethod = Literal['left', 'center', 'right']
VerticalAlignMethod = Literal['top', 'middle', 'bottom']

def _align_fit_segments(lines: list, new_line: Segment) -> Iterable[Segment]:
    for line in lines:
        yield from line
        yield new_line

def _align_left_segments(excess_space: int, lines: list, style: Optional['StyleType'], pad: bool, new_line: Segment) -> Iterable[Segment]:
    pad_segment = Segment(' ' * excess_space, style) if pad else None
    for line in lines:
        yield from line
        if pad_segment:
            yield pad_segment
        yield new_line

def _align_center_segments(excess_space: int, lines: list, style: Optional['StyleType'], pad: bool, new_line: Segment) -> Iterable[Segment]:
    left = excess_space // 2
    left_pad = Segment(' ' * left, style)
    pad_right = Segment(' ' * (excess_space - left), style) if pad else None
    for line in lines:
        if left:
            yield left_pad
        yield from line
        if pad_right:
            yield pad_right
        yield new_line

def _align_right_segments(excess_space: int, lines: list, style: Optional['StyleType'], new_line: Segment) -> Iterable[Segment]:
    pad_segment = Segment(' ' * excess_space, style)
    for line in lines:
        yield pad_segment
        yield from line
        yield new_line

def _align_generate_segments(align: AlignMethod, excess_space: int, lines: list, style: Optional['StyleType'], pad: bool, new_line: Segment) -> Iterable[Segment]:
    if excess_space <= 0:
        yield from _align_fit_segments(lines, new_line)
        return
    if align == 'left':
        yield from _align_left_segments(excess_space, lines, style, pad, new_line)
        return
    if align == 'center':
        yield from _align_center_segments(excess_space, lines, style, pad, new_line)
        return
    yield from _align_right_segments(excess_space, lines, style, new_line)

def _align_blank_lines(count: int, blank_line: Segment) -> Iterable[Segment]:
    if count > 0:
        for _ in range(count):
            yield blank_line

def _align_vertical_segments(vertical: VerticalAlignMethod, vertical_height: int, height: int, lines: list, style: Optional['StyleType'], pad: bool, new_line: Segment, align: AlignMethod, excess_space: int, blank_line: Segment) -> Iterable[Segment]:
    segments = _align_generate_segments(align, excess_space, lines, style, pad, new_line)
    if vertical == 'top':
        bottom_space = vertical_height - height
        return chain(segments, _align_blank_lines(bottom_space, blank_line))
    if vertical == 'middle':
        top_space = (vertical_height - height) // 2
        bottom_space = vertical_height - top_space - height
        return chain(_align_blank_lines(top_space, blank_line), segments, _align_blank_lines(bottom_space, blank_line))
    top_space = vertical_height - height
    return chain(_align_blank_lines(top_space, blank_line), segments)

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


    def __init__(self, renderable: 'RenderableType', align: AlignMethod='left', style: Optional[StyleType]=None, *, vertical: Optional[VerticalAlignMethod]=None, pad: bool=True, width: Optional[int]=None, height: Optional[int]=None) -> None:
        if align not in ('left', 'center', 'right'):
            raise ValueError(f'invalid value for align, expected "left", "center", or "right" (not {align!r})')
        if vertical is not None and vertical not in ('top', 'middle', 'bottom'):
            raise ValueError(f'invalid value for vertical, expected "top", "middle", or "bottom" (not {vertical!r})')
        self.renderable = renderable
        self.align = align
        self.style = style
        self.vertical = vertical
        self.pad = pad
        self.width = width
        self.height = height

    def __repr__(self) -> str:
        return f'Align({self.renderable!r}, {self.align!r})'

    @classmethod
    def left(cls, renderable: 'RenderableType', style: Optional[StyleType]=None, *, vertical: Optional[VerticalAlignMethod]=None, pad: bool=True, width: Optional[int]=None, height: Optional[int]=None) -> 'Align':
        """Align a renderable to the left."""
        return cls(renderable, 'left', style=style, vertical=vertical, pad=pad, width=width, height=height)

    @classmethod
    def center(cls, renderable: 'RenderableType', style: Optional[StyleType]=None, *, vertical: Optional[VerticalAlignMethod]=None, pad: bool=True, width: Optional[int]=None, height: Optional[int]=None) -> 'Align':
        """Align a renderable to the center."""
        return cls(renderable, 'center', style=style, vertical=vertical, pad=pad, width=width, height=height)

    @classmethod
    def right(cls, renderable: 'RenderableType', style: Optional[StyleType]=None, *, vertical: Optional[VerticalAlignMethod]=None, pad: bool=True, width: Optional[int]=None, height: Optional[int]=None) -> 'Align':
        """Align a renderable to the right."""
        return cls(renderable, 'right', style=style, vertical=vertical, pad=pad, width=width, height=height)

    def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> 'RenderResult':
        align = self.align
        width = console.measure(self.renderable, options=options).maximum
        rendered = console.render(Constrain(self.renderable, width if self.width is None else min(width, self.width)), options.update(height=None))
        lines = list(Segment.split_lines(rendered))
        width, height = Segment.get_shape(lines)
        lines = Segment.set_shape(lines, width, height)
        new_line = Segment.line()
        excess_space = options.max_width - width
        style = console.get_style(self.style) if self.style is not None else None
        blank_line = Segment(f"{' ' * (self.width or options.max_width)}\n", style) if self.pad else Segment('\n')
        vertical_height = self.height or options.height
        if self.vertical and vertical_height is not None:
            iter_segments = _align_vertical_segments(self.vertical, vertical_height, height, lines, style, self.pad, new_line, align, excess_space, blank_line)
        else:
            iter_segments = _align_generate_segments(align, excess_space, lines, style, self.pad, new_line)
        if self.style:
            style = console.get_style(self.style)
            iter_segments = Segment.apply_style(iter_segments, style)
        yield from iter_segments

    def __rich_measure__(self, console: 'Console', options: 'ConsoleOptions') -> Measurement:
        measurement = Measurement.get(console, options, self.renderable)
        return measurement

class VerticalCenter(JupyterMixin):
    """Vertically aligns a renderable.

    Warn:
        This class is deprecated and may be removed in a future version. Use Align class with
        `vertical="middle"`.

    Args:
        renderable (RenderableType): A renderable object.
        style (StyleType, optional): An optional style to apply to the background. Defaults to None.
    """



    def __init__(self, renderable: 'RenderableType', style: Optional[StyleType]=None) -> None:
        self.renderable = renderable
        self.style = style

    def __repr__(self) -> str:
        return f'VerticalCenter({self.renderable!r})'

    def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> 'RenderResult':
        style = console.get_style(self.style) if self.style is not None else None
        lines = console.render_lines(self.renderable, options.update(height=None), pad=False)
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

    def __rich_measure__(self, console: 'Console', options: 'ConsoleOptions') -> Measurement:
        measurement = Measurement.get(console, options, self.renderable)
        return measurement