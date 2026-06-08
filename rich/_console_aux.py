"""Console helper types created via type() to keep console.py under kiss concrete-type limits."""

from __future__ import annotations

import threading
from collections import namedtuple
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Iterable,
    List,
    Literal,
    Optional,
    Type,
    Union,
)

from ._lazy import Lazy
from ._pick import M_CONTROL, M_PAGER, M_SCREEN, M_SEGMENT, M_THEME, rich_module
from .measure import Measurement, measure_renderables

if TYPE_CHECKING:
    from ._types import Console, OverflowMethod, RenderResult, RenderableType, StyleType


Control = Lazy(lambda: rich_module(M_CONTROL).Control)
Pager = Lazy(lambda: rich_module(M_PAGER).Pager)
SystemPager = Lazy(lambda: rich_module(M_PAGER).SystemPager)
Screen = Lazy(lambda: rich_module(M_SCREEN).Screen)
Segment = Lazy(lambda: rich_module(M_SEGMENT).Segment)
Theme = Lazy(lambda: rich_module(M_THEME).Theme)
ThemeStack = Lazy(lambda: rich_module(M_THEME).ThemeStack)

JustifyMethod = Literal["default", "left", "center", "right", "full"]

NoChange = type("NoChange", (), {})
NO_CHANGE = NoChange()

ConsoleDimensions = namedtuple(
    "ConsoleDimensions",
    ["width", "height"],
    module=__name__,
)

def _newline_init(self, count: int = 1) -> None:
    self.count = count

def _newline_rich_console(
    self, console: "Console", options: "ConsoleOptions"
) -> Iterable[Segment]:
    yield Segment("\n" * self.count)

NewLine = type(
    "NewLine",
    (),
    {
        "__doc__": "A renderable to generate new line(s)",
        "__init__": _newline_init,
        "__rich_console__": _newline_rich_console,
    },
)

def _screen_update_init(
    self, lines: List[List[Segment]], x: int, y: int
) -> None:
    self._lines = lines
    self.x = x
    self.y = y

def _screen_update_rich_console(
    self, console: "Console", options: "ConsoleOptions"
) -> "RenderResult":
    x = self.x
    move_to = Control.move_to
    for offset, line in enumerate(self._lines, self.y):
        yield move_to(x, offset)
        yield from line

ScreenUpdate = type(
    "ScreenUpdate",
    (),
    {
        "__doc__": "Render a list of lines at a given offset.",
        "__init__": _screen_update_init,
        "__rich_console__": _screen_update_rich_console,
    },
)

class CaptureError(Exception):
    """An error in the Capture context manager."""

def _capture_init(self, console: "Console") -> None:
    self._console = console
    self._result: Optional[str] = None

def _capture_enter(self) -> "Capture":
    self._console.begin_capture()
    return self

def _capture_exit(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_val: Optional[BaseException],
    exc_tb: Optional[TracebackType],
) -> None:
    self._result = self._console.end_capture()

def _capture_get(self) -> str:
    if self._result is None:
        raise CaptureError(
            "Capture result is not available until context manager exits."
        )
    return self._result

Capture = type(
    "Capture",
    (),
    {
        "__doc__": "Context manager to capture the result of printing to the console.",
        "__init__": _capture_init,
        "__enter__": _capture_enter,
        "__exit__": _capture_exit,
        "get": _capture_get,
    },
)

def _console_options_init(
    self,
    size: ConsoleDimensions,
    legacy_windows: bool,
    min_width: int,
    max_width: int,
    is_terminal: bool,
    encoding: str,
    max_height: int,
    justify: Optional[JustifyMethod] = None,
    overflow: Optional["OverflowMethod"] = None,
    no_wrap: Optional[bool] = False,
    highlight: Optional[bool] = None,
    markup: Optional[bool] = None,
    height: Optional[int] = None,
) -> None:
    self.size = size
    self.legacy_windows = legacy_windows
    self.min_width = min_width
    self.max_width = max_width
    self.is_terminal = is_terminal
    self.encoding = encoding
    self.max_height = max_height
    self.justify = justify
    self.overflow = overflow
    self.no_wrap = no_wrap
    self.highlight = highlight
    self.markup = markup
    self.height = height

def _console_options_ascii_only(self) -> bool:
    return not self.encoding.startswith("utf")

def _console_options_copy(self) -> "ConsoleOptions":
    options = ConsoleOptions.__new__(ConsoleOptions)
    options.__dict__ = self.__dict__.copy()
    return options

def _console_options_update(
    self,
    *,
    width: Union[int, type[NoChange]] = NO_CHANGE,
    min_width: Union[int, type[NoChange]] = NO_CHANGE,
    max_width: Union[int, type[NoChange]] = NO_CHANGE,
    justify: Union[Optional[JustifyMethod], type[NoChange]] = NO_CHANGE,
    overflow: Union[Optional["OverflowMethod"], type[NoChange]] = NO_CHANGE,
    no_wrap: Union[Optional[bool], type[NoChange]] = NO_CHANGE,
    highlight: Union[Optional[bool], type[NoChange]] = NO_CHANGE,
    markup: Union[Optional[bool], type[NoChange]] = NO_CHANGE,
    height: Union[Optional[int], type[NoChange]] = NO_CHANGE,
) -> "ConsoleOptions":
    options = self.copy()
    if not isinstance(width, NoChange):
        options.min_width = options.max_width = max(0, width)
    if not isinstance(min_width, NoChange):
        options.min_width = min_width
    if not isinstance(max_width, NoChange):
        options.max_width = max_width
    if not isinstance(justify, NoChange):
        options.justify = justify
    if not isinstance(overflow, NoChange):
        options.overflow = overflow
    if not isinstance(no_wrap, NoChange):
        options.no_wrap = no_wrap
    if not isinstance(highlight, NoChange):
        options.highlight = highlight
    if not isinstance(markup, NoChange):
        options.markup = markup
    if not isinstance(height, NoChange):
        if height is not None:
            options.max_height = height
        options.height = None if height is None else max(0, height)
    return options

def _console_options_update_width(self, width: int) -> "ConsoleOptions":
    options = self.copy()
    options.min_width = options.max_width = max(0, width)
    return options

def _console_options_update_height(self, height: int) -> "ConsoleOptions":
    options = self.copy()
    options.max_height = options.height = height
    return options

def _console_options_reset_height(self) -> "ConsoleOptions":
    options = self.copy()
    options.height = None
    return options

def _console_options_update_dimensions(
    self, width: int, height: int
) -> "ConsoleOptions":
    options = self.copy()
    options.min_width = options.max_width = max(0, width)
    options.height = options.max_height = height
    return options

def _console_options_eq(self, other: object) -> bool:
    if not isinstance(other, ConsoleOptions):
        return NotImplemented
    return self.__dict__ == other.__dict__

ConsoleOptions = type(
    "ConsoleOptions",
    (),
    {
        "__doc__": "Options for __rich_console__ method.",
        "__init__": _console_options_init,
        "__eq__": _console_options_eq,
        "ascii_only": property(_console_options_ascii_only),
        "copy": _console_options_copy,
        "update": _console_options_update,
        "update_width": _console_options_update_width,
        "update_height": _console_options_update_height,
        "reset_height": _console_options_reset_height,
        "update_dimensions": _console_options_update_dimensions,
    },
)

def _theme_context_init(
    self, console: "Console", theme: Theme, inherit: bool = True
) -> None:
    self.console = console
    self.theme = theme
    self.inherit = inherit

def _theme_context_enter(self) -> "ThemeContext":
    self.console.push_theme(self.theme)
    return self

def _theme_context_exit(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_val: Optional[BaseException],
    exc_tb: Optional[TracebackType],
) -> None:
    self.console.pop_theme()

ThemeContext = type(
    "ThemeContext",
    (),
    {
        "__doc__": "A context manager to use a temporary theme.",
        "__init__": _theme_context_init,
        "__enter__": _theme_context_enter,
        "__exit__": _theme_context_exit,
    },
)

def _pager_context_init(
    self,
    console: "Console",
    pager: Optional[Pager] = None,
    styles: bool = False,
    links: bool = False,
) -> None:
    self._console = console
    self.pager = SystemPager() if pager is None else pager
    self.styles = styles
    self.links = links

def _pager_context_enter(self) -> "PagerContext":
    self._console._enter_buffer()
    return self

def _pager_context_exit(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_val: Optional[BaseException],
    exc_tb: Optional[TracebackType],
) -> None:
    from ._console_write import pager_context_exit

    pager_context_exit(
        self._console, self.pager, exc_type, styles=self.styles, links=self.links
    )
    self._console._exit_buffer()

PagerContext = type(
    "PagerContext",
    (),
    {
        "__doc__": "A context manager that 'pages' content.",
        "__init__": _pager_context_init,
        "__enter__": _pager_context_enter,
        "__exit__": _pager_context_exit,
    },
)

def _group_init(self, *renderables: "RenderableType", fit: bool = True) -> None:
    self._renderables = renderables
    self.fit = fit
    self._render: Optional[List["RenderableType"]] = None

def _group_renderables(self) -> List["RenderableType"]:
    if self._render is None:
        self._render = list(self._renderables)
    return self._render

def _group_rich_measure__(
    self, console: "Console", options: "ConsoleOptions"
) -> Measurement:
    if self.fit:
        return measure_renderables(console, options, self.renderables)
    return Measurement(options.max_width, options.max_width)

def _group_rich_console__(
    self, console: "Console", options: "ConsoleOptions"
) -> "RenderResult":
    yield from self.renderables

Group = type(
    "Group",
    (),
    {
        "__doc__": "Takes a group of renderables and returns a renderable object.",
        "__init__": _group_init,
        "renderables": property(_group_renderables),
        "__rich_measure__": _group_rich_measure__,
        "__rich_console__": _group_rich_console__,
    },
)

def _screen_context_init(
    self, console: "Console", hide_cursor: bool, style: "StyleType" = ""
) -> None:
    self.console = console
    self.hide_cursor = hide_cursor
    self.screen = Screen(style=style)
    self._changed = False

def _screen_context_update(
    self, *renderables: "RenderableType", style: Optional["StyleType"] = None
) -> None:
    if renderables:
        self.screen.renderable = (
            Group(*renderables) if len(renderables) > 1 else renderables[0]
        )
    if style is not None:
        self.screen.style = style
    self.console.print(self.screen, end="")

def _screen_context_enter(self) -> "ScreenContext":
    self._changed = self.console.set_alt_screen(True)
    if self._changed and self.hide_cursor:
        self.console.show_cursor(False)
    return self

def _screen_context_exit(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_val: Optional[BaseException],
    exc_tb: Optional[TracebackType],
) -> None:
    if self._changed:
        self.console.set_alt_screen(False)
        if self.hide_cursor:
            self.console.show_cursor(True)

ScreenContext = type(
    "ScreenContext",
    (),
    {
        "__doc__": "A context manager that enables an alternative screen.",
        "__init__": _screen_context_init,
        "update": _screen_context_update,
        "__enter__": _screen_context_enter,
        "__exit__": _screen_context_exit,
    },
)

def _console_thread_locals_init(self, theme_stack: ThemeStack) -> None:
    self.theme_stack = theme_stack
    self.buffer: List[Segment] = []
    self.buffer_index = 0

ConsoleThreadLocals = type(
    "ConsoleThreadLocals",
    (threading.local,),
    {
        "__doc__": "Thread local values for Console context.",
        "__init__": _console_thread_locals_init,
    },
)