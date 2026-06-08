from __future__ import annotations

from collections import defaultdict
from itertools import chain
from operator import itemgetter
from typing import Dict, Iterable, List, Optional, Tuple, Union, TYPE_CHECKING

from ._align_types import AlignMethod
from ._jupyter_mixin import JupyterMixin
from ._lazy import Lazy
from ._padding_dims import PaddingDimensions
from ._pick import M_ALIGN, M_CONSOLE, M_PADDING, M_TABLE, rich_module
from .constrain import Constrain
from .measure import Measurement

if TYPE_CHECKING:
    from ._types import ConsoleOptions, RenderResult, RenderableType, Text


TextType = Union[str, "Text"]


def _Align():
    return rich_module(M_ALIGN).Align


def _Console():
    return rich_module(M_CONSOLE).Console


def _Padding():
    return rich_module(M_PADDING).Padding


def _Table():
    return rich_module(M_TABLE).Table


Align = Lazy(_Align)
Console = Lazy(_Console)
Padding = Lazy(_Padding)
Table = Lazy(_Table)


def _columns_iter_column_first(
    width_renderables: List[Tuple[int, "RenderableType"]],
    item_count: int,
    column_count: int,
) -> Iterable[Tuple[int, "RenderableType"]]:
    column_lengths: List[int] = [item_count // column_count] * column_count
    for col_no in range(item_count % column_count):
        column_lengths[col_no] += 1

    row_count = (item_count + column_count - 1) // column_count
    cells = [[-1] * column_count for _ in range(row_count)]
    row = col = 0
    for index in range(item_count):
        cells[row][col] = index
        column_lengths[col] -= 1
        if column_lengths[col]:
            row += 1
        else:
            col += 1
            row = 0
    for index in chain.from_iterable(cells):
        if index == -1:
            break
        yield width_renderables[index]


def _columns_iter_renderables(
    column_first: bool,
    renderable_widths: List[int],
    renderables: List["RenderableType"],
    column_count: int,
) -> Iterable[Tuple[int, Optional[RenderableType]]]:
    item_count = len(renderables)
    if column_first:
        width_renderables = list(zip(renderable_widths, renderables))
        yield from _columns_iter_column_first(
            width_renderables, item_count, column_count
        )
    else:
        yield from zip(renderable_widths, renderables)
    if item_count % column_count:
        for _ in range(column_count - (item_count % column_count)):
            yield 0, None


def _columns_compute_column_count(
    width: Optional[int],
    max_width: int,
    width_padding: int,
    renderable_widths: List[int],
    column_first: bool,
    renderables: List["RenderableType"],
) -> int:
    if width is not None:
        return max(max_width // (width + width_padding), 1)
    column_count = len(renderables)
    widths: Dict[int, int] = defaultdict(int)
    while column_count > 1:
        widths.clear()
        column_no = 0
        for renderable_width, _ in _columns_iter_renderables(
            column_first, renderable_widths, renderables, column_count
        ):
            widths[column_no] = max(widths[column_no], renderable_width)
            total_width = sum(widths.values()) + width_padding * (len(widths) - 1)
            if total_width > max_width:
                column_count = len(widths) - 1
                break
            column_no = (column_no + 1) % column_count
        else:
            break
    return column_count


def _columns_prepare_renderables(
    column_first: bool,
    renderable_widths: List[int],
    renderables: List["RenderableType"],
    column_count: int,
    equal: bool,
    align: Optional[AlignMethod],
) -> List[Optional["RenderableType"]]:
    get_renderable = itemgetter(1)
    prepared = [
        get_renderable(item)
        for item in _columns_iter_renderables(
            column_first, renderable_widths, renderables, column_count
        )
    ]
    if equal:
        fixed_width = renderable_widths[0]
        prepared = [
            None if renderable is None else Constrain(renderable, fixed_width)
            for renderable in prepared
        ]
    if align:
        _Align = Align
        prepared = [
            None if renderable is None else _Align(renderable, align)
            for renderable in prepared
        ]
    return prepared


def _columns_add_rows(
    table: "Table",
    prepared: list,
    column_count: int,
    right_to_left: bool,
) -> None:
    """Add prepared renderables to the grid table in row order."""
    add_row = table.add_row
    for start in range(0, len(prepared), column_count):
        row = prepared[start : start + column_count]
        if right_to_left:
            row = row[::-1]
        add_row(*row)


def _columns_rich_console(
    columns: "Columns",
    console: "Console",
    options: "ConsoleOptions",
) -> "RenderResult":
    render_str = console.render_str
    renderables = [
        render_str(renderable) if isinstance(renderable, str) else renderable
        for renderable in columns.renderables
    ]
    if not renderables:
        return
    _top, right, _bottom, left = Padding.unpack(columns.padding)
    width_padding = max(left, right)
    max_width = options.max_width
    get_measurement = Measurement.get
    renderable_widths = [
        get_measurement(console, options, renderable).maximum
        for renderable in renderables
    ]
    if columns.equal:
        renderable_widths = [max(renderable_widths)] * len(renderable_widths)

    table = Table.grid(padding=columns.padding, collapse_padding=True, pad_edge=False)
    table.expand = columns.expand
    table.title = columns.title

    if columns.width is not None:
        column_count = (max_width) // (columns.width + width_padding)
        for _ in range(column_count):
            table.add_column(width=columns.width)
    else:
        column_count = _columns_compute_column_count(
            columns.width,
            max_width,
            width_padding,
            renderable_widths,
            columns.column_first,
            renderables,
        )

    prepared = _columns_prepare_renderables(
        columns.column_first,
        renderable_widths,
        renderables,
        column_count,
        columns.equal,
        columns.align,
    )
    _columns_add_rows(table, prepared, column_count, columns.right_to_left)
    yield table


class Columns(JupyterMixin):
    """Display renderables in neat columns.

    Args:
        renderables (Iterable[RenderableType]): Any number of Rich renderables (including str).
        width (int, optional): The desired width of the columns, or None to auto detect. Defaults to None.
        padding (PaddingDimensions, optional): Optional padding around cells. Defaults to (0, 1).
        expand (bool, optional): Expand columns to full width. Defaults to False.
        equal (bool, optional): Arrange in to equal sized columns. Defaults to False.
        column_first (bool, optional): Align items from top to bottom (rather than left to right). Defaults to False.
        right_to_left (bool, optional): Start column from right hand side. Defaults to False.
        align (str, optional): Align value ("left", "right", or "center") or None for default. Defaults to None.
        title (TextType, optional): Optional title for Columns.
    """

    def __init__(
        self,
        renderables: Optional[Iterable["RenderableType"]] = None,
        padding: PaddingDimensions = (0, 1),
        *,
        width: Optional[int] = None,
        expand: bool = False,
        equal: bool = False,
        column_first: bool = False,
        right_to_left: bool = False,
        align: Optional[AlignMethod] = None,
        title: Optional[TextType] = None,
    ) -> None:
        self.renderables = list(renderables or [])
        self.width = width
        self.padding = padding
        self.expand = expand
        self.equal = equal
        self.column_first = column_first
        self.right_to_left = right_to_left
        self.align: Optional[AlignMethod] = align
        self.title = title

    def add_renderable(self, renderable: "RenderableType") -> None:
        """Add a renderable to the columns.

        Args:
            renderable (RenderableType): Any renderable object.
        """
        self.renderables.append(renderable)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield from _columns_rich_console(self, console, options)


if __name__ == "__main__":  # pragma: no cover
    import importlib
    import os

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    console = importlib.import_module(_pkg + ".console").Console()

    files = [f"{i} {s}" for i, s in enumerate(sorted(os.listdir()))]
    columns = Columns(files, padding=(0, 1), expand=False, equal=False)
    console.print(columns)
    console.rule()
    columns.column_first = True
    console.print(columns)
    columns.right_to_left = True
    console.rule()
    console.print(columns)
