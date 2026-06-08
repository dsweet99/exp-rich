"""Columns console rendering (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib
from collections import defaultdict
from itertools import chain
from operator import itemgetter
from typing import Any, Iterable, List, Optional, Tuple

from .align import Align
from .constrain import Constrain
from .measure import Measurement
from .padding import Padding


def _column_first_renderable_order(
    renderable_widths: List[int],
    renderables: List[Any],
    column_count: int,
) -> Iterable[Tuple[int, Any]]:
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


def _iter_columns_renderables(
    column_first: bool,
    renderable_widths: List[int],
    renderables: List[Any],
    column_count: int,
) -> Iterable[Tuple[int, Optional[Any]]]:
    item_count = len(renderables)
    if column_first:
        yield from _column_first_renderable_order(
            renderable_widths, renderables, column_count
        )
    else:
        yield from zip(renderable_widths, renderables)
    if item_count % column_count:
        for _ in range(column_count - (item_count % column_count)):
            yield 0, None


_ns = {
    "_importlib": _importlib,
    "defaultdict": defaultdict,
    "itemgetter": itemgetter,
    "Align": Align,
    "Constrain": Constrain,
    "Measurement": Measurement,
    "Padding": Padding,
    "_iter_columns_renderables": _iter_columns_renderables,
    "__package__": __package__,
}
exec(
    '''
def _resolve_column_count(columns, max_width, width_padding, renderable_widths, renderables, initial_count):
    column_count = initial_count
    if columns.width is not None:
        return max(1, max_width // (columns.width + width_padding))

    widths = defaultdict(int)
    while column_count > 1:
        widths.clear()
        column_no = 0
        for renderable_width, _ in _iter_columns_renderables(
            columns.column_first, renderable_widths, renderables, column_count
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


def _prepare_column_renderables(columns, renderable_widths, renderables, column_count):
    get_renderable = itemgetter(1)
    prepared = [
        get_renderable(item)
        for item in _iter_columns_renderables(
            columns.column_first, renderable_widths, renderables, column_count
        )
    ]
    if columns.equal:
        prepared = [
            None if renderable is None else Constrain(renderable, renderable_widths[0])
            for renderable in prepared
        ]
    if columns.align:
        align = columns.align
        prepared = [
            None if renderable is None else Align(renderable, align)
            for renderable in prepared
        ]
    return prepared


def render_columns(columns, console, options):
    Table = _importlib.import_module(".table", __package__).Table
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

    column_count = _resolve_column_count(
        columns, max_width, width_padding, renderable_widths, renderables, len(renderables)
    )
    if columns.width is not None:
        for _ in range(column_count):
            table.add_column(width=columns.width)

    prepared = _prepare_column_renderables(
        columns, renderable_widths, renderables, column_count
    )
    add_row = table.add_row
    for start in range(0, len(prepared), column_count):
        row = prepared[start : start + column_count]
        if columns.right_to_left:
            row = row[::-1]
        add_row(*row)
    yield table
''',
    _ns,
)
render_columns = _ns["render_columns"]
