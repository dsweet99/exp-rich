from datetime import datetime
from typing import Any, Callable, Iterable, List, Optional, Union

from ._log_types import FormatTimeCallable
from ._runtime import get_table_class, get_text_class

TextType = Union[str, Any]


def _format_log_time(
    console: "Console",
    log_time: Optional[datetime],
    time_format: Optional[Union[str, FormatTimeCallable]],
    default_time_format: Union[str, FormatTimeCallable],
) -> Any:
    Text = get_text_class()

    log_time = log_time or console.get_datetime()
    time_format = time_format or default_time_format
    if callable(time_format):
        return time_format(log_time)
    return Text(log_time.strftime(time_format))


def _build_path_text(path: str, line_no: Optional[int], link_path: Optional[str]) -> Any:
    Text = get_text_class()

    path_text = Text()
    path_text.append(path, style=f"link file://{link_path}" if link_path else "")
    if line_no:
        path_text.append(":")
        path_text.append(
            f"{line_no}",
            style=f"link file://{link_path}#{line_no}" if link_path else "",
        )
    return path_text


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
        self._last_time: Optional[Any] = None

    def _append_time_column(
        self,
        row: List["RenderableType"],
        console: "Console",
        log_time: Optional[datetime],
        time_format: Optional[Union[str, FormatTimeCallable]],
    ) -> None:
        Text = get_text_class()

        log_time_display = _format_log_time(
            console, log_time, time_format, self.time_format
        )
        if log_time_display == self._last_time and self.omit_repeated_times:
            row.append(Text(" " * len(log_time_display)))
        else:
            row.append(log_time_display)
            self._last_time = log_time_display

    def __call__(
        self,
        console: "Console",
        renderables: Iterable["ConsoleRenderable"],
        log_time: Optional[datetime] = None,
        time_format: Optional[Union[str, FormatTimeCallable]] = None,
        level: TextType = "",
        path: Optional[str] = None,
        line_no: Optional[int] = None,
        link_path: Optional[str] = None,
    ) -> Any:
        from ._runtime import _mod

        Renderables = _mod("rich.containers").Renderables
        Table = get_table_class()

        output = Table.grid(padding=(0, 1))
        output.expand = True
        if self.show_time:
            output.add_column(style="log.time")
        if self.show_level:
            output.add_column(style="log.level", width=self.level_width)
        output.add_column(ratio=1, style="log.message", overflow="fold")
        if self.show_path and path:
            output.add_column(style="log.path")
        row: List["RenderableType"] = []
        if self.show_time:
            self._append_time_column(row, console, log_time, time_format)
        if self.show_level:
            row.append(level)
        row.append(Renderables(renderables))
        if self.show_path and path:
            row.append(_build_path_text(path, line_no, link_path))
        output.add_row(*row)
        return output
