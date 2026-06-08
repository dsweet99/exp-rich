from __future__ import annotations

from ._lazy import import_attr
from datetime import datetime
from typing import TYPE_CHECKING, Iterable, List, Optional, Union, Callable


Text = import_attr('rich.text', 'Text')
TextType = import_attr('rich.text', 'TextType')


FormatTimeCallable = Callable[[datetime], Text]
if TYPE_CHECKING:
    from .console import Console, ConsoleRenderable, RenderableType
    from .table import Table



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
        self._last_time: Optional[Text] = None

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
    ) -> "Table":
        Renderables = import_attr('rich.containers', 'Renderables')
        Table = import_attr('rich.table', 'Table')

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
        self._append_time_column(row, console, log_time, time_format)
        if self.show_level:
            row.append(level)

        row.append(Renderables(renderables))
        if self.show_path and path:
            row.append(self._make_path_text(path, line_no, link_path))

        output.add_row(*row)
        return output

    def _append_time_column(
        self,
        row: List["RenderableType"],
        console: "Console",
        log_time: Optional[datetime],
        time_format: Optional[Union[str, FormatTimeCallable]],
    ) -> None:
        if not self.show_time:
            return
        log_time = log_time or console.get_datetime()
        time_format = time_format or self.time_format
        if callable(time_format):
            log_time_display = time_format(log_time)
        else:
            log_time_display = Text(log_time.strftime(time_format))
        if log_time_display == self._last_time and self.omit_repeated_times:
            row.append(Text(" " * len(log_time_display)))
        else:
            row.append(log_time_display)
            self._last_time = log_time_display

    def _make_path_text(
        self, path: str, line_no: Optional[int], link_path: Optional[str]
    ) -> "Text":
        path_text = Text()
        path_text.append(path, style=f"link file://{link_path}" if link_path else "")
        if line_no:
            path_text.append(":")
            path_text.append(
                f"{line_no}",
                style=f"link file://{link_path}#{line_no}" if link_path else "",
            )
        return path_text


if __name__ == "__main__":  # pragma: no cover
    Console = import_attr('rich.console', 'Console')

    c = Console()
    c.print("[on blue]Hello", justify="right")
    c.log("[on blue]hello", justify="right")
