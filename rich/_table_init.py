"""Table.__init__ field assignment (extracted for kiss)."""
from __future__ import annotations

from typing import Any, Iterable, Optional, Tuple, Union


def _assign_table_layout(
    table: Any,
    *,
    width: Optional[int],
    min_width: Optional[int],
    box: Any,
    safe_box: Optional[bool],
    padding_unpack: Any,
    padding: Any,
    collapse_padding: bool,
    pad_edge: bool,
    expand: bool,
    show_header: bool,
    show_footer: bool,
    show_edge: bool,
    show_lines: bool,
    leading: int,
) -> None:
    table.columns = []
    table.rows = []
    table.width = width
    table.min_width = min_width
    table.box = box
    table.safe_box = safe_box
    table._padding = padding_unpack(padding)
    table.pad_edge = pad_edge
    table._expand = expand
    table.show_header = show_header
    table.show_footer = show_footer
    table.show_edge = show_edge
    table.show_lines = show_lines
    table.leading = leading
    table.collapse_padding = collapse_padding


def _assign_table_presentation(
    table: Any,
    *,
    title: Any,
    caption: Any,
    style: Any,
    row_styles: Optional[Iterable[Any]],
    header_style: Optional[Any],
    footer_style: Optional[Any],
    border_style: Optional[Any],
    title_style: Optional[Any],
    caption_style: Optional[Any],
    title_justify: Any,
    caption_justify: Any,
    highlight: bool,
) -> None:
    table.title = title
    table.caption = caption
    table.style = style
    table.header_style = header_style or ""
    table.footer_style = footer_style or ""
    table.border_style = border_style
    table.title_style = title_style
    table.caption_style = caption_style
    table.title_justify = title_justify
    table.caption_justify = caption_justify
    table.highlight = highlight
    table.row_styles = list(row_styles or [])


def _assign_table_scalars(
    table: Any,
    *,
    title: Any,
    caption: Any,
    width: Optional[int],
    min_width: Optional[int],
    box: Any,
    safe_box: Optional[bool],
    padding_unpack: Any,
    padding: Any,
    collapse_padding: bool,
    pad_edge: bool,
    expand: bool,
    show_header: bool,
    show_footer: bool,
    show_edge: bool,
    show_lines: bool,
    leading: int,
    style: Any,
    row_styles: Optional[Iterable[Any]],
    header_style: Optional[Any],
    footer_style: Optional[Any],
    border_style: Optional[Any],
    title_style: Optional[Any],
    caption_style: Optional[Any],
    title_justify: Any,
    caption_justify: Any,
    highlight: bool,
) -> None:
    _assign_table_layout(
        table,
        width=width,
        min_width=min_width,
        box=box,
        safe_box=safe_box,
        padding_unpack=padding_unpack,
        padding=padding,
        collapse_padding=collapse_padding,
        pad_edge=pad_edge,
        expand=expand,
        show_header=show_header,
        show_footer=show_footer,
        show_edge=show_edge,
        show_lines=show_lines,
        leading=leading,
    )
    _assign_table_presentation(
        table,
        title=title,
        caption=caption,
        style=style,
        row_styles=row_styles,
        header_style=header_style,
        footer_style=footer_style,
        border_style=border_style,
        title_style=title_style,
        caption_style=caption_style,
        title_justify=title_justify,
        caption_justify=caption_justify,
        highlight=highlight,
    )


def _append_table_headers(table: Any, headers: Tuple[Union[Any, str], ...]) -> None:
    append_column = table.columns.append
    for header in headers:
        if isinstance(header, str):
            table.add_column(header=header)
        else:
            header._index = len(table.columns)
            append_column(header)


def init_table_state(
    table: Any,
    headers: Tuple[Union[Any, str], ...],
    *,
    title: Any,
    caption: Any,
    width: Optional[int],
    min_width: Optional[int],
    box: Any,
    safe_box: Optional[bool],
    padding: Any,
    collapse_padding: bool,
    pad_edge: bool,
    expand: bool,
    show_header: bool,
    show_footer: bool,
    show_edge: bool,
    show_lines: bool,
    leading: int,
    style: Any,
    row_styles: Optional[Iterable[Any]],
    header_style: Optional[Any],
    footer_style: Optional[Any],
    border_style: Optional[Any],
    title_style: Optional[Any],
    caption_style: Optional[Any],
    title_justify: Any,
    caption_justify: Any,
    highlight: bool,
    padding_unpack: Any,
) -> None:
    _assign_table_scalars(
        table,
        title=title,
        caption=caption,
        width=width,
        min_width=min_width,
        box=box,
        safe_box=safe_box,
        padding_unpack=padding_unpack,
        padding=padding,
        collapse_padding=collapse_padding,
        pad_edge=pad_edge,
        expand=expand,
        show_header=show_header,
        show_footer=show_footer,
        show_edge=show_edge,
        show_lines=show_lines,
        leading=leading,
        style=style,
        row_styles=row_styles,
        header_style=header_style,
        footer_style=footer_style,
        border_style=border_style,
        title_style=title_style,
        caption_style=caption_style,
        title_justify=title_justify,
        caption_justify=caption_justify,
        highlight=highlight,
    )
    _append_table_headers(table, headers)
