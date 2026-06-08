from __future__ import annotations

from ._lazy import import_attr
from collections import defaultdict
from itertools import chain
from operator import itemgetter
from typing import Callable, Dict, Iterable, List, Optional, Tuple

Align = import_attr('rich.align', 'Align')
AlignMethod = import_attr('rich.align', 'AlignMethod')
Console = import_attr('rich.console', 'Console')
ConsoleOptions = import_attr('rich.console', 'ConsoleOptions')
RenderableType = import_attr('rich.console', 'RenderableType')
RenderResult = import_attr('rich.console', 'RenderResult')
Constrain = import_attr('rich.constrain', 'Constrain')
Measurement = import_attr('rich.measure', 'Measurement')
Padding = import_attr('rich.padding', 'Padding')
PaddingDimensions = import_attr('rich.padding', 'PaddingDimensions')
Table = import_attr('rich.table', 'Table')
TextType = import_attr('rich.text', 'TextType')
JupyterMixin = import_attr('rich.jupyter', 'JupyterMixin')


def _columns_column_first_order(
    item_count: int, column_count: int
) -> Iterable[int]:
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
        yield index


def _columns_iter_renderables(
    *,
    column_first: bool,
    column_count: int,
    renderable_widths: List[int],
    renderables: List[RenderableType],
) -> Iterable[Tuple[int, Optional[RenderableType]]]:
    item_count = len(renderables)
    if column_first:
        width_renderables = list(zip(renderable_widths, renderables))
        for index in _columns_column_first_order(item_count, column_count):
            yield width_renderables[index]
    else:
        yield from zip(renderable_widths, renderables)
    if item_count % column_count:
        for _ in range(column_count - (item_count % column_count)):
            yield 0, None


def _columns_fit_column_count(
    *,
    column_count: int,
    max_width: int,
    width_padding: int,
    widths: Dict[int, int],
    iter_renderables: Callable[[], Iterable[Tuple[int, Optional[RenderableType]]]],
) -> int:
    while column_count > 1:
        widths.clear()
        column_no = 0
        for renderable_width, _ in iter_renderables():
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
    renderables: List[RenderableType],
    *,
    equal: bool,
    align: Optional[AlignMethod],
    renderable_widths: List[int],
) -> List[Optional[RenderableType]]:
    get_renderable = itemgetter(1)
    prepared = [get_renderable(item) for item in renderables]
    if equal:
        prepared = [
            None if renderable is None else Constrain(renderable, renderable_widths[0])
            for renderable in prepared
        ]
    if align:
        _Align = Align
        prepared = [
            None if renderable is None else _Align(renderable, align)
            for renderable in prepared
        ]
    return prepared


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

    def _columns_renderable_widths(
        self, console: Console, options: ConsoleOptions, renderables: List[RenderableType]
    ) -> List[int]:
        get_measurement = Measurement.get
        renderable_widths = [
            get_measurement(console, options, renderable).maximum
            for renderable in renderables
        ]
        if self.equal:
            renderable_widths = [max(renderable_widths)] * len(renderable_widths)
        return renderable_widths

    def _columns_build_table(
        self,
        *,
        max_width: int,
        width_padding: int,
        column_count: int,
        renderable_widths: List[int],
        renderables: List[RenderableType],
        widths: Dict[int, int],
    ) -> Table:
        table = Table.grid(padding=self.padding, collapse_padding=True, pad_edge=False)
        table.expand = self.expand
        table.title = self.title

        def iter_items(count: int) -> Iterable[Tuple[int, Optional[RenderableType]]]:
            return _columns_iter_renderables(
                column_first=self.column_first,
                column_count=count,
                renderable_widths=renderable_widths,
                renderables=renderables,
            )

        if self.width is not None:
            column_count = max_width // (self.width + width_padding)
            for _ in range(column_count):
                table.add_column(width=self.width)
        else:
            column_count = _columns_fit_column_count(
                column_count=column_count,
                max_width=max_width,
                width_padding=width_padding,
                widths=widths,
                iter_renderables=lambda: iter_items(column_count),
            )

        prepared = _columns_prepare_renderables(
            list(iter_items(column_count)),
            equal=self.equal,
            align=self.align,
            renderable_widths=renderable_widths,
        )
        add_row = table.add_row
        for start in range(0, len(prepared), column_count):
            row = prepared[start : start + column_count]
            if self.right_to_left:
                row = row[::-1]
            add_row(*row)
        return table

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        render_str = console.render_str
        renderables = [
            render_str(renderable) if isinstance(renderable, str) else renderable
            for renderable in self.renderables
        ]
        if not renderables:
            return
        _top, right, _bottom, left = Padding.unpack(self.padding)
        width_padding = max(left, right)
        widths: Dict[int, int] = defaultdict(int)
        renderable_widths = self._columns_renderable_widths(
            console, options, renderables
        )
        yield self._columns_build_table(
            max_width=options.max_width,
            width_padding=width_padding,
            column_count=len(renderables),
            renderable_widths=renderable_widths,
            renderables=renderables,
            widths=widths,
        )


if __name__ == "__main__":  # pragma: no cover
    import os

    console = Console()

    files = [f"{i} {s}" for i, s in enumerate(sorted(os.listdir()))]
    columns = Columns(files, padding=(0, 1), expand=False, equal=False)
    console.print(columns)
    console.rule()
    columns.column_first = True
    console.print(columns)
    columns.right_to_left = True
    console.rule()
    console.print(columns)
