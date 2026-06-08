from __future__ import annotations

from collections import defaultdict
from itertools import chain
from operator import itemgetter
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Tuple, Union

from .align import Align, AlignMethod
from .constrain import Constrain
from .measure import Measurement
from .padding import Padding, PaddingDimensions
from ._jupyter_mixin import JupyterMixin
from ._runtime import get_table_class

if TYPE_CHECKING:
    from .console import Console, ConsoleOptions, RenderableType, RenderResult
    from .table import Table

TextType = Union[str, "Text"]


def _columns_column_first_items(
    column_count: int,
    renderable_widths: List[int],
    renderables: List[RenderableType],
) -> Iterable[Tuple[int, Optional[RenderableType]]]:
    item_count = len(renderables)
    width_renderables = list(zip(renderable_widths, renderables))
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
    column_count: int,
    renderable_widths: List[int],
    renderables: List[RenderableType],
) -> Iterable[Tuple[int, Optional[RenderableType]]]:
    item_count = len(renderables)
    if column_first:
        yield from _columns_column_first_items(
            column_count, renderable_widths, renderables
        )
    else:
        yield from zip(renderable_widths, renderables)
    if item_count % column_count:
        for _ in range(column_count - (item_count % column_count)):
            yield 0, None


def _columns_fit_column_count(
    columns: Columns,
    column_count: int,
    max_width: int,
    width_padding: int,
    renderable_widths: List[int],
    renderables: List[RenderableType],
) -> int:
    widths: Dict[int, int] = defaultdict(int)
    while column_count > 1:
        widths.clear()
        column_no = 0
        for renderable_width, _ in _columns_iter_renderables(
            columns.column_first, column_count, renderable_widths, renderables
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


def _columns_prepare_rows(
    columns: Columns,
    column_count: int,
    renderable_widths: List[int],
    renderables: List[RenderableType],
) -> List[Optional[RenderableType]]:
    get_renderable = itemgetter(1)
    rows = [
        get_renderable(item)
        for item in _columns_iter_renderables(
            columns.column_first, column_count, renderable_widths, renderables
        )
    ]
    if columns.equal:
        rows = [
            None if renderable is None else Constrain(renderable, renderable_widths[0])
            for renderable in rows
        ]
    if columns.align:
        align = columns.align
        rows = [
            None if renderable is None else Align(renderable, align)
            for renderable in rows
        ]
    return rows


def _columns_make_grid(
    columns: Columns,
    max_width: int,
    width_padding: int,
    column_count: int,
    renderable_widths: List[int],
    renderables: List[RenderableType],
) -> tuple[Table, int]:
    Table = get_table_class()
    table = Table.grid(padding=columns.padding, collapse_padding=True, pad_edge=False)
    table.expand = columns.expand
    table.title = columns.title
    if columns.width is not None:
        column_count = max_width // (columns.width + width_padding)
        for _ in range(column_count):
            table.add_column(width=columns.width)
    else:
        column_count = _columns_fit_column_count(
            columns, column_count, max_width, width_padding, renderable_widths, renderables
        )
    return table, column_count


def _columns_build_table(
    columns: Columns,
    console: Console,
    options: ConsoleOptions,
) -> Optional[Table]:
    renderables = [
        console.render_str(renderable) if isinstance(renderable, str) else renderable
        for renderable in columns.renderables
    ]
    if not renderables:
        return None
    _top, right, _bottom, left = Padding.unpack(columns.padding)
    width_padding = max(left, right)
    max_width = options.max_width
    renderable_widths = [
        Measurement.get(console, options, renderable).maximum
        for renderable in renderables
    ]
    if columns.equal:
        renderable_widths = [max(renderable_widths)] * len(renderable_widths)
    column_count = len(renderables)
    table, column_count = _columns_make_grid(
        columns, max_width, width_padding, column_count, renderable_widths, renderables
    )
    rows = _columns_prepare_rows(columns, column_count, renderable_widths, renderables)
    add_row = table.add_row
    for start in range(0, len(rows), column_count):
        row = rows[start : start + column_count]
        if columns.right_to_left:
            row = row[::-1]
        add_row(*row)
    return table


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
        renderables: Optional[Iterable[RenderableType]] = None,
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

    def add_renderable(self, renderable: RenderableType) -> None:
        """Add a renderable to the columns.

        Args:
            renderable (RenderableType): Any renderable object.
        """
        self.renderables.append(renderable)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        table = _columns_build_table(self, console, options)
        if table is not None:
            yield table
