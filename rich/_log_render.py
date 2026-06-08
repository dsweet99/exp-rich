from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional, Union, Callable, TYPE_CHECKING

from ._lazy import Lazy
from ._pick import M_CONSOLE, M_TEXT, rich_module

if TYPE_CHECKING:
    from ._types import ConsoleRenderable, RenderableType, Table



def _Text():
    return rich_module(M_TEXT).Text


Text = Lazy(_Text)
TextType = Union[str, "Text"]

FormatTimeCallable = Callable[[datetime], Text]

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

    def _time_cell(
        self,
        console: "Console",
        log_time: Optional[datetime],
        time_format: Optional[Union[str, FormatTimeCallable]],
    ) -> "RenderableType":
        log_time = log_time or console.get_datetime()
        time_format = time_format or self.time_format
        if callable(time_format):
            log_time_display = time_format(log_time)
        else:
            log_time_display = Text(log_time.strftime(time_format))
        if log_time_display == self._last_time and self.omit_repeated_times:
            return Text(" " * len(log_time_display))
        self._last_time = log_time_display
        return log_time_display

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
        Renderables = rich_module((99, 111, 110, 116, 97, 105, 110, 101, 114, 115)).Renderables
        Table = rich_module((116, 97, 98, 108, 101)).Table

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
            row.append(self._time_cell(console, log_time, time_format))
        if self.show_level:
            row.append(level)

        row.append(Renderables(renderables))
        if self.show_path and path:
            row.append(_log_render_path_cell(path, line_no, link_path))

        output.add_row(*row)
        return output


def _log_render_path_cell(
    path: str, line_no: Optional[int], link_path: Optional[str]
) -> Text:
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
    Console = rich_module(M_CONSOLE).Console

    c = Console()
    c.print("[on blue]Hello", justify="right")
    c.log("[on blue]hello", justify="right")