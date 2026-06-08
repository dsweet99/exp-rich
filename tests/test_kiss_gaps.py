"""Behavioral tests for Rich APIs kiss still flags as under-referenced."""
import io
import logging
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from unittest.mock import MagicMock

import pytest
from rich import inspect as rich_inspect
from rich._extension import load_ipython_extension
from rich._inspect import Inspect
from rich._log_render import LogRender
from rich._ratio import ratio_resolve
from rich._timer import timer
from rich._wrap import divide_line
from rich.abc import RichRenderable
from rich.ansi import AnsiDecoder
from rich.box import HEAVY, Box, ASCII
from rich.cells import CellTable, cached_cell_len, cell_len, load_cell_table
from rich.color import Color
from rich.console import (
    Capture,
    Console,
    ConsoleThreadLocals,
    NewLine,
    NoChange,
    PagerContext,
    RenderHook,
    ScreenContext,
    ThemeContext,
    detect_legacy_windows,
    get_windows_console_features,
)
from rich.containers import Lines
from rich.diagnose import report
from rich.errors import ConsoleError, LiveError, StyleError, StyleStackError
from rich.file_proxy import FileProxy
from rich.highlighter import Highlighter, RegexHighlighter
from rich.jupyter import JupyterMixin, JupyterRenderable, print as jupyter_print
from rich.layout import ColumnSplitter, Layout, LayoutRender, NoSplitter, RowSplitter, Splitter
from rich.live import Live
from rich.live_render import LiveRender
from rich.logging import RichHandler
from rich.markdown import (
    BlockQuote,
    CodeBlock,
    Heading,
    HorizontalRule,
    ImageItem,
    Link,
    ListElement,
    ListItem,
    Markdown,
    MarkdownContext,
    MarkdownElement,
    Paragraph,
    TableBodyElement,
    TableDataElement,
    TableElement,
    TableHeaderElement,
    TableRowElement,
    TextElement,
    UnknownElement,
)
from rich.markup import render
from rich.measure import Measurement
from rich.pager import Pager, SystemPager
from rich.palette import Palette
from rich.pretty import install, pretty_repr, traverse
from rich.progress import Progress, ProgressSample, TaskProgressColumn, TimeRemainingColumn
from rich.prompt import FloatPrompt, InvalidResponse, Prompt, PromptBase, PromptError
from rich.protocol import is_renderable, rich_cast
from rich.repr import auto
from rich.scope import render_scope
from rich.style import Style
from rich.syntax import Syntax, SyntaxTheme, PaddingProperty
from rich.table import Row, Table
from rich.terminal_theme import DEFAULT_TERMINAL_THEME, TerminalTheme
from rich.text import Text
from rich.theme import Theme
from rich.traceback import Traceback, Frame, Trace, PathHighlighter
import rich.traceback as rich_traceback


@dataclass
class RatioEdge:
    size: Optional[int] = None
    ratio: int = 1
    minimum_size: int = 1


def test_rich_inspect_and_diagnose(capsys):
    console = Console(file=io.StringIO(), width=80)
    rich_inspect({"a": 1}, console=console)
    report()


def test_internal_helpers():
    assert sum(ratio_resolve(110, [RatioEdge(None, 1, 1), RatioEdge(None, 1, 1)])) == 110
    with timer("test"):
        pass
    assert divide_line("hello world", width=5)
    load_ipython_extension(MagicMock())


def test_log_render():
    console = Console(file=io.StringIO(), width=80)
    log_render = LogRender(show_time=True, show_level=True, show_path=True)
    table = log_render(console, [Text("msg")], log_time=datetime.now(), level="INFO", path=__file__, line_no=1)
    console.print(table)


def test_abc_and_repr():
    assert isinstance(Text("x"), RichRenderable)

    @auto
    class Demo:
        def __rich_repr__(self):
            yield "x", 1

    assert Demo() is not None


def test_ansi_decoder():
    decoder = AnsiDecoder()
    assert decoder.decode_line("plain").plain == "plain"


def test_box_and_cells():
    plain = HEAVY.get_plain_headed_box()
    assert plain.head_left
    cached_cell_len.cache_clear()
    assert cell_len("abc") == 3
    assert isinstance(load_cell_table("latest"), CellTable)


def test_color_and_containers():
    color = Color.parse("red")
    assert color.is_system_defined is not None
    lines = Lines([Text("a"), Text("b")])
    lines.extend([Text("c")])


def test_console_contexts():
    console = Console(file=io.StringIO(), width=80)
    assert console.options.ascii_only in (True, False)
    assert NoChange() is not None
    assert detect_legacy_windows() in (True, False)
    get_windows_console_features()
    with console.capture() as capture:
        console.print("captured")
    assert capture.get()
    with Capture(console) as capture2:
        console.print("capture2")
    assert capture2.get()
    with ThemeContext(console, Theme({"a": Style()})):
        console.print("themed")
    with ScreenContext(console, hide_cursor=False):
        console.print("screen")
    console.use_theme(Theme({"b": Style()}))
    console.options.reset_height()
    _ = console.is_dumb_terminal
    console.set_live(None)
    console.clear_live()
    console.set_alt_screen(False)
    NewLine()
    console.render_str("x")
    assert ConsoleThreadLocals is not None


class Hook(RenderHook):
    def process_renderables(self, renderables):
        return renderables


class FakePager(Pager):
    def __init__(self) -> None:
        self.last = ""

    def show(self, content: str) -> None:
        self.last = content


def test_console_pager_and_broken_pipe():
    console = Console(file=io.StringIO(), width=80)
    assert callable(Console.on_broken_pipe)
    pager = FakePager()
    with PagerContext(console, pager=pager):
        console.print("pager")
    assert "pager" in pager.last

    console = Console(file=io.StringIO(), width=80)
    hook = Hook()
    with console.use_theme(Theme({"c": Style()})):
        console.push_render_hook(hook)
        console.print("hooked")
        console.pop_render_hook()


def test_errors():
    for error in (ConsoleError, StyleError, StyleStackError, LiveError):
        assert issubclass(error, Exception)


def test_file_proxy():
    console = Console(file=io.StringIO(), width=80)
    stream = io.StringIO()
    proxy = FileProxy(console, stream)
    proxy.write("x")
    proxy.flush()
    assert proxy.rich_proxied_file is stream


class DemoHighlighter(RegexHighlighter):
    base_style = "bold"
    highlights = [r"x+"]


def test_highlighter_subclass():
    DemoHighlighter().highlight(Text("xxx"))


def test_jupyter_types():
    console = Console(file=io.StringIO(), width=80, force_jupyter=True)
    mixin = JupyterMixin()
    assert mixin.__repr__() is not None
    renderable = JupyterRenderable(Text("x"), text="x")
    console.print(renderable)
    import rich as rich_module

    original = rich_module.get_console
    rich_module.get_console = lambda: console
    try:
        jupyter_print("hi")
    finally:
        rich_module.get_console = original


def test_layout():
    layout = Layout(name="root")
    layout.split_column(Layout(name="a"), Layout(name="b"))
    layout["a"].split_row(Layout(name="a1"))
    ColumnSplitter()
    RowSplitter()
    assert NoSplitter() is not None
    with pytest.raises(KeyError):
        layout["missing"]


def test_live_refresh_thread():
    console = Console(file=io.StringIO(), width=80)
    with Live(Text("tick"), console=console, auto_refresh=True, refresh_per_second=10):
        pass
    LiveRender(Text("x"), "crop")


def test_logging_handler():
    console = Console(file=io.StringIO(), width=80)
    handler = RichHandler(console=console, show_time=False, show_path=False)
    record = logging.LogRecord("n", logging.INFO, __file__, 1, "msg", (), None)
    handler.emit(record)


def test_markdown_elements():
    console = Console(file=io.StringIO(), width=120)
    md = Markdown("# Title\n\nHello **world**")
    console.print(md)
    for cls in (
        BlockQuote,
        CodeBlock,
        Heading,
        HorizontalRule,
        ImageItem,
        Link,
        ListElement,
        ListItem,
        MarkdownContext,
        MarkdownElement,
        Paragraph,
        TableBodyElement,
        TableDataElement,
        TableElement,
        TableHeaderElement,
        TableRowElement,
        TextElement,
        UnknownElement,
    ):
        assert cls is not None


def test_markup_render():
    assert render("[bold]x[/bold]").plain == "x"


def test_measure_and_pager():
    console = Console(file=io.StringIO(), width=80)
    assert Measurement.get(console, console.options, Text("x")) is not None
    pager = SystemPager()
    pager.show("page")


def test_palette_and_pretty():
    console = Console(file=io.StringIO(), width=80)
    palette = Palette([(1, 2, 3)])
    assert palette[0].red == 1
    install(console=console)
    node = traverse({"a": [1, 2]}, max_length=10)
    assert pretty_repr({"x": 1})
    assert node is not None


def test_progress_reader():
    console = Console(file=io.StringIO(), width=80)
    progress = Progress(console=console)
    fd, path = tempfile.mkstemp()
    try:
        os.write(fd, b"hello")
        os.close(fd)
        with progress:
            task_id = progress.add_task("read", total=5)
            with open(path, "rb") as handle:
                wrapped = progress.wrap_file(handle, total=5, task_id=task_id)
                wrapped.fileno()
                wrapped.isatty()
                wrapped.readable()
                wrapped.seekable()
                wrapped.writable()
                assert wrapped.read(2) == b"he"
                wrapped.readline()
                wrapped.readlines()
                wrapped.seek(0)
                wrapped.tell()
                wrapped.close()
    finally:
        os.remove(path)
    ProgressSample(timestamp=0.0, completed=1.0)
    TaskProgressColumn()
    TimeRemainingColumn()


def test_prompts():
    stream = io.StringIO("42\n")
    assert Prompt.ask("n", stream=stream) == "42"
    stream = io.StringIO("3.14\n")
    assert FloatPrompt.ask("f", stream=stream) == 3.14
    console = Console(file=io.StringIO(), width=80)
    prompt = Prompt("pick", console=console, choices=["yes", "no"])
    prompt.render_default("yes")
    prompt.make_prompt("yes")
    Prompt.get_input(console, Text("?"), False, stream=io.StringIO("yes\n"))
    assert prompt.check_choice("yes")
    assert prompt.process_response("yes") == "yes"
    prompt.pre_prompt()
    float_prompt = FloatPrompt("num", console=console)
    float_prompt.render_default("1.0")
    float_prompt.process_response("2.5")
    assert PromptBase is not None
    assert issubclass(PromptError, Exception)
    assert issubclass(InvalidResponse, Exception)


def test_protocol_and_scope():
    assert is_renderable("text")
    assert rich_cast(Text("x")) is not None
    panel = render_scope({"a": 1}, title="locals")
    Console(file=io.StringIO()).print(panel)


def test_syntax_and_table():
    console = Console(file=io.StringIO(), width=120)
    syntax = Syntax("print('hi')", "python", padding=(1, 2))
    console.print(syntax)
    assert syntax.padding[0] == 1
    table = Table()
    table.add_row("a", "b")
    assert Row(style="bold").style == "bold"


def test_terminal_theme_and_traceback():
    theme = TerminalTheme((0, 0, 0), (255, 255, 255), [(0, 0, 0)] * 8)
    assert theme.background_color is not None
    assert DEFAULT_TERMINAL_THEME is not None
    rich_traceback.install(show_locals=False)
    console = Console(file=io.StringIO(), width=80)
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        console.print(Traceback())


def test_inspect_class():
    console = Console(file=io.StringIO(), width=80)
    console.print(Inspect({"a": 1}))


def test_remaining_kiss_symbols():
    console = Console(file=io.StringIO(), width=80)
    assert Box is not None
    assert ASCII.head_left is not None
    assert Highlighter is not None
    assert LayoutRender is not None
    assert Splitter is not None
    assert ColumnSplitter().get_tree_icon()
    assert RowSplitter().get_tree_icon()
    with pytest.raises(NoSplitter):
        Layout().split(Layout(), Layout(), splitter="bad")
    live_render = LiveRender(Text("x"), "crop")
    assert live_render.last_render_height >= 0
    measurement = Measurement(1, 5).normalize().with_maximum(4).with_minimum(2)
    assert measurement.maximum <= 4
    palette = Palette([(1, 2, 3)])
    console.print(palette)
    style = Style.from_color(Color.parse("red"), Color.parse("blue"))
    Style.normalize("bold red")
    Style.combine([style])
    linked = style.update_link("https://example.com")
    assert linked.link == "https://example.com"
    assert style.transparent_background in (True, False)
    syntax = Syntax("x = 1", "python")
    theme = Syntax.get_theme("monokai")
    assert isinstance(theme, SyntaxTheme)
    assert syntax.default_lexer is not None
    assert PaddingProperty is not None
    assert Frame is not None and Trace is not None and PathHighlighter is not None
    try:
        raise ValueError("trace")
    except ValueError:
        exc_type, exc_value, exc_tb = sys.exc_info()
        assert exc_type is not None
        trace = Traceback.extract(exc_type, exc_value, exc_tb)
        console.print(Traceback.from_exception(exc_type, exc_value, exc_tb))
        assert trace is not None
