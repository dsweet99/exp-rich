from __future__ import annotations

from datetime import datetime
from typing import Callable, Iterable, List, Optional, Union

from ._render_factory import renderables as make_renderables
from ._render_factory import table_grid
from .text import Text as TextType
from ._render_protocol import Console, ConsoleRenderable, RenderableType, Table

FormatTimeCallable = Callable[[datetime], TextType]


def format_log_time_display(
    log_time: datetime,
    time_format: Union[str, FormatTimeCallable],
    text_cls: type,
) -> TextType:
    """Format a log timestamp for display."""
    if callable(time_format):
        return time_format(log_time)
    return text_cls(log_time.strftime(time_format))


def append_log_time(
    row: List[RenderableType],
    *,
    log_time: datetime,
    time_format: Union[str, FormatTimeCallable],
    omit_repeated_times: bool,
    last_time: Optional[TextType],
    text_cls: type,
) -> Optional[TextType]:
    """Append the time column; return the new last_time display."""
    log_time_display = format_log_time_display(log_time, time_format, text_cls)
    if log_time_display == last_time and omit_repeated_times:
        row.append(text_cls(" " * len(log_time_display)))
        return last_time
    row.append(log_time_display)
    return log_time_display


def append_log_path(
    row: List[RenderableType],
    *,
    path: str,
    line_no: Optional[int],
    link_path: Optional[str],
    text_cls: type,
) -> None:
    """Append the path column to a log row."""
    path_text = text_cls()
    path_text.append(path, style=f"link file://{link_path}" if link_path else "")
    if line_no:
        path_text.append(":")
        path_text.append(
            f"{line_no}",
            style=f"link file://{link_path}#{line_no}" if link_path else "",
        )
    row.append(path_text)


def build_log_table(
    log_render: object,
    console: Console,
    renderables: Iterable[ConsoleRenderable],
    *,
    log_time: Optional[datetime],
    time_format: Optional[Union[str, FormatTimeCallable]],
    level: TextType,
    path: Optional[str],
    line_no: Optional[int],
    link_path: Optional[str],
    table_grid_fn: Callable[..., Table],
    make_renderables_fn: Callable[..., RenderableType],
    text_cls: type,
) -> Table:
    """Build the log table for a LogRender call."""
    output = table_grid_fn(padding=(0, 1))
    output.expand = True
    if log_render.show_time:
        output.add_column(style="log.time")
    if log_render.show_level:
        output.add_column(style="log.level", width=log_render.level_width)
    output.add_column(ratio=1, style="log.message", overflow="fold")
    if log_render.show_path and path:
        output.add_column(style="log.path")

    row: List[RenderableType] = []
    if log_render.show_time:
        log_render._last_time = append_log_time(
            row,
            log_time=log_time or console.get_datetime(),
            time_format=time_format or log_render.time_format,
            omit_repeated_times=log_render.omit_repeated_times,
            last_time=log_render._last_time,
            text_cls=text_cls,
        )
    if log_render.show_level:
        row.append(level)
    row.append(make_renderables_fn(renderables))
    if log_render.show_path and path:
        append_log_path(
            row,
            path=path,
            line_no=line_no,
            link_path=link_path,
            text_cls=text_cls,
        )
    output.add_row(*row)
    return output


class LogRender:
    def __init__(
        self,
        show_time: bool = True,
        show_level: bool = False,
        show_path: bool = True,
        time_format: Union[str, FormatTimeCallable] = "[%x %X]",
        omit_repeated_times: bool = True,
        level_width: Optional[int] = 8,
    ) -> None:
        self.show_time = show_time
        self.show_level = show_level
        self.show_path = show_path
        self.time_format = time_format
        self.omit_repeated_times = omit_repeated_times
        self.level_width = level_width
        self._last_time: Optional[TextType] = None

    def __call__(
        self,
        console: Console,
        renderables: Iterable[ConsoleRenderable],
        log_time: Optional[datetime] = None,
        time_format: Optional[Union[str, FormatTimeCallable]] = None,
        level: TextType = "",
        path: Optional[str] = None,
        line_no: Optional[int] = None,
        link_path: Optional[str] = None,
    ) -> Table:
        return build_log_table(
            self,
            console,
            renderables,
            log_time=log_time,
            time_format=time_format,
            level=level,
            path=path,
            line_no=line_no,
            link_path=link_path,
            table_grid_fn=table_grid,
            make_renderables_fn=make_renderables,
            text_cls=TextType,
        )


from ._log_render_registry import register_log_render  # noqa: E402

register_log_render(LogRender)
