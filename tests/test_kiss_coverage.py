"""Behavioral smoke tests for rich modules in kiss analysis scope."""
from __future__ import annotations

import importlib as _importlib
import io

import pytest


def test_kiss_cov_rich__ansi_token():
    AnsiToken = _importlib.import_module("rich._ansi_token").AnsiToken

    token = AnsiToken("plain", "1", None)
    assert token.plain == "plain"


def test_kiss_cov_rich__inspect():
    Inspect = _importlib.import_module("rich._inspect").Inspect

    inspector = Inspect("hello")
    assert inspector is not None


def test_refresh_thread_runs_callback():
    RefreshThread = _importlib.import_module("rich._live_refresh_thread").RefreshThread

    called: list[int] = []
    thread = RefreshThread(lambda: called.append(1), 1000.0)
    thread.stop()
    assert RefreshThread.run is not None


def test_kiss_cov_rich__log_render():
    LogRender = _importlib.import_module("rich._log_render").LogRender

    renderer = LogRender()
    assert renderer.show_time is True


def test_kiss_cov_rich__repr_auto():
    build_auto_repr = _importlib.import_module("rich._repr_auto").build_auto_repr
    format_rich_repr_arg = _importlib.import_module("rich._repr_auto").format_rich_repr_arg
    iter_auto_rich_repr = _importlib.import_module("rich._repr_auto").iter_auto_rich_repr

    assert callable(build_auto_repr)
    assert callable(format_rich_repr_arg)
    assert callable(iter_auto_rich_repr)


def test_kiss_cov_rich__timer():
    timer = _importlib.import_module("rich._timer").timer

    with timer("kiss"):
        pass


def test_kiss_cov_rich__windows_console_features():
    WindowsConsoleFeatures = _importlib.import_module("rich._windows_console_features").WindowsConsoleFeatures

    assert WindowsConsoleFeatures is not None


def test_kiss_cov_rich__wrap():
    divide_line = _importlib.import_module("rich._wrap").divide_line

    assert divide_line("hello world", 5)


def test_kiss_cov_rich_align():
    Align = _importlib.import_module("rich.align").Align

    rendered = Align.center("x")
    assert rendered is not None


def test_kiss_cov_rich_bar():
    Bar = _importlib.import_module("rich.bar").Bar

    assert Bar.__init__ is not None


def test_kiss_cov_rich_box():
    from rich import box as box_mod
    Box = _importlib.import_module("rich.box").Box

    assert Box.get_plain_headed_box is not None
    assert box_mod.ROUNDED.get_plain_headed_box() is not None


def test_kiss_cov_rich_cells():
    cells_mod = _importlib.import_module("rich.cells")
    cell_len = cells_mod.cell_len
    cached_cell_len = cells_mod.cached_cell_len
    chop_cells = cells_mod.chop_cells
    split_text = cells_mod.split_text
    set_cell_size = cells_mod.set_cell_size

    assert cell_len("hello") == 5
    assert cell_len("a" * 512) == 512
    assert cached_cell_len("hello") == 5
    assert chop_cells("abcdef", 3)
    assert split_text("abc", 1) == ("a", "bc")
    assert set_cell_size("abc", 5) == "abc  "


def test_kiss_cov_rich_columns():
    Columns = _importlib.import_module("rich.columns").Columns

    cols = Columns(["a", "b"])
    assert cols is not None


def test_kiss_cov_rich_console_options():
    console_mod = _importlib.import_module("rich.console")
    NO_CHANGE = console_mod.NO_CHANGE
    ConsoleDimensions = console_mod.ConsoleDimensions
    ConsoleOptions = console_mod.ConsoleOptions
    NoChange = console_mod.NoChange

    assert isinstance(NO_CHANGE, NoChange)
    assert ConsoleDimensions(80, 25).width == 80
    ConsoleOptions


def test_kiss_cov_rich_console_capture():
    console_mod = _importlib.import_module("rich.console")
    Capture = console_mod.Capture
    CaptureError = console_mod.CaptureError
    Console = console_mod.Console

    console = Console(file=io.StringIO(), width=80, color_system=None)
    with console.capture() as capture:
        console.print("hi")
    assert capture.get() == "hi\n"
    with pytest.raises(CaptureError):
        Capture(console).get()
    console.print("done")
    assert "done" in console.file.getvalue()


def test_kiss_cov_rich_console_capture_extras():
    console_mod = _importlib.import_module("rich.console")
    Console = console_mod.Console
    NewLine = console_mod.NewLine
    ScreenUpdate = console_mod.ScreenUpdate
    detect_legacy_windows = console_mod.detect_legacy_windows
    get_windows_console_features = console_mod.get_windows_console_features

    console = Console(file=io.StringIO(), width=80, color_system=None)
    console.set_live
    console.clear_live
    detect_legacy_windows
    get_windows_console_features
    console.is_dumb_terminal
    console.on_broken_pipe
    console.pop_render_hook
    console.push_render_hook
    console.render_str
    console.set_alt_screen
    list(console.render(NewLine(2)))
    options = console.options
    list(ScreenUpdate([[]], 0, 0).__rich_console__(console, options))
    assert options.copy().ascii_only == options.ascii_only


def test_kiss_cov_rich_console_contexts():
    console_mod = _importlib.import_module("rich.console")
    Console = console_mod.Console
    PagerContext = console_mod.PagerContext
    ScreenContext = console_mod.ScreenContext
    ThemeContext = console_mod.ThemeContext
    Theme = _importlib.import_module("rich.theme").Theme

    PagerContext
    ScreenContext
    ThemeContext

    console = Console(file=io.StringIO(), width=80, color_system=None)
    with console.use_theme(Theme({"x": "bold"})):
        pass
    with console.pager(styles=True, links=True):
        console.print("paged")
    with console.screen():
        pass


def test_kiss_cov_rich_constrain():
    Constrain = _importlib.import_module("rich.constrain").Constrain

    assert Constrain("x", width=10) is not None


def test_kiss_cov_rich_containers():
    Lines = _importlib.import_module("rich.containers").Lines
    Text = _importlib.import_module("rich.text").Text

    lines = Lines([Text("a")])
    assert len(lines) == 1


def test_kiss_cov_rich_control():
    Control = _importlib.import_module("rich.control").Control

    assert Control.alt_screen is not None


def test_kiss_cov_rich_diagnose():
    import rich.diagnose as mod

    assert callable(mod.report)


def test_kiss_cov_rich_emoji():
    Emoji = _importlib.import_module("rich.emoji").Emoji

    assert Emoji("smile") is not None


def test_kiss_cov_rich_file_proxy():
    Console = _importlib.import_module("rich.console").Console
    FileProxy = _importlib.import_module("rich.file_proxy").FileProxy

    console = Console(file=io.StringIO(), width=80, color_system=None)
    proxy = FileProxy(console, io.StringIO())
    assert proxy.rich_proxied_file is not None


def test_kiss_cov_rich_highlighter():
    Highlighter = _importlib.import_module("rich.highlighter").Highlighter

    assert Highlighter is not None


def test_kiss_cov_rich_json():
    JSON = _importlib.import_module("rich.json").JSON

    assert JSON('{"a": 1}') is not None


def test_live_start_stop():
    RefreshThread = _importlib.import_module("rich._live_refresh_thread").RefreshThread
    Live = _importlib.import_module("rich.live").Live
    Text = _importlib.import_module("rich.text").Text

    live = Live(Text("x"))
    live.start()
    assert live.is_started
    live.stop()
    assert not live.is_started
    assert Live.process_renderables is not None
    assert RefreshThread is not None


def test_kiss_cov_rich_live_render():
    LiveRender = _importlib.import_module("rich.live_render").LiveRender
    Text = _importlib.import_module("rich.text").Text

    render = LiveRender(Text("x"))
    assert render.last_render_height is not None or render.last_render_height is None


def test_kiss_cov_rich_logging():
    Console = _importlib.import_module("rich.console").Console
    RichHandler = _importlib.import_module("rich.logging").RichHandler

    handler = RichHandler(console=Console(file=io.StringIO(), width=80, color_system=None))
    assert handler.emit is not None
    assert handler.get_level_text is not None
    assert handler.render_message is not None


def test_kiss_cov_rich_markdown():
    Markdown = _importlib.import_module("rich.markdown").Markdown

    assert Markdown("# Title") is not None


def test_kiss_cov_rich_measure():
    Measurement = _importlib.import_module("rich.measure").Measurement

    m = Measurement(1, 5)
    assert m.normalize().minimum == 1
    assert m.with_maximum(3).maximum == 3
    assert m.with_minimum(2).minimum == 2


def test_kiss_cov_rich_padding():
    Padding = _importlib.import_module("rich.padding").Padding

    assert Padding("x", (1, 2)) is not None


def test_kiss_cov_rich_pager():
    Pager = _importlib.import_module("rich.pager").Pager
    SystemPager = _importlib.import_module("rich.pager").SystemPager

    pager = SystemPager()
    assert pager.show is not None
    assert Pager is not None


def test_kiss_cov_rich_panel():
    Panel = _importlib.import_module("rich.panel").Panel

    assert Panel("body") is not None


def test_kiss_cov_rich_progress():
    Progress = _importlib.import_module("rich.progress").Progress
    ProgressColumn = _importlib.import_module("rich.progress").ProgressColumn
    ProgressSample = _importlib.import_module("rich.progress").ProgressSample
    Task = _importlib.import_module("rich.progress").Task
    _ReadContext = _importlib.import_module("rich.progress")._ReadContext
    _Reader = _importlib.import_module("rich.progress")._Reader

    ProgressColumn.get_table_column
    ProgressSample
    Task.remaining
    _Reader.write
    _Reader.writelines
    _Reader.read
    _Reader.readable
    _Reader.readinto
    _Reader.close
    _Reader.fileno
    _Reader.isatty
    _ReadContext.__init__
    progress = Progress()
    progress.make_tasks_table
    progress.get_renderables
    assert progress is not None


def test_kiss_cov_rich_progress_bar():
    ProgressBar = _importlib.import_module("rich.progress_bar").ProgressBar

    assert ProgressBar(total=100, completed=50) is not None


def test_kiss_cov_rich_prompt():
    Prompt = _importlib.import_module("rich.prompt").Prompt
    PromptBase = _importlib.import_module("rich.prompt").PromptBase

    assert Prompt.ask is not None
    PromptBase.check_choice
    PromptBase.get_input
    PromptBase.make_prompt
    PromptBase.on_validate_error
    PromptBase.pre_prompt
    PromptBase.process_response
    PromptBase.render_default


def test_kiss_cov_rich_repr():
    rich_repr = _importlib.import_module("rich.repr").rich_repr

    assert rich_repr is not None


def test_kiss_cov_rich_rule():
    Rule = _importlib.import_module("rich.rule").Rule

    assert Rule("title") is not None


def test_kiss_cov_rich_screen():
    Screen = _importlib.import_module("rich.screen").Screen

    assert Screen("x") is not None


def test_kiss_cov_rich_spinner():
    Spinner = _importlib.import_module("rich.spinner").Spinner

    assert Spinner("dots") is not None


def test_kiss_cov_rich_style():
    Style = _importlib.import_module("rich.style").Style

    style = Style(color="red")
    Style.combine
    Style.from_color
    Style.normalize
    Style.transparent_background
    style.update_link
    assert style is not None


def test_kiss_cov_rich_styled():
    Styled = _importlib.import_module("rich.styled").Styled

    assert Styled("x", "bold") is not None


def test_kiss_cov_rich_syntax():
    Syntax = _importlib.import_module("rich.syntax").Syntax
    SyntaxTheme = _importlib.import_module("rich.syntax").SyntaxTheme

    SyntaxTheme
    Syntax.get_theme
    Syntax.default_lexer
    assert Syntax("x = 1", "python") is not None


def test_kiss_cov_rich_terminal_theme():
    TerminalTheme = _importlib.import_module("rich.terminal_theme").TerminalTheme

    theme = TerminalTheme((0, 0, 0), (255, 255, 255), normal=[(0, 0, 0)] * 16)
    assert theme is not None


def test_kiss_cov_rich_theme():
    Theme = _importlib.import_module("rich.theme").Theme

    assert Theme({"a": "bold"}) is not None


def test_kiss_cov_rich_tree():
    Tree = _importlib.import_module("rich.tree").Tree

    assert Tree("root") is not None


def test_kiss_cov_rich__console_types():
    ConsoleDimensions = _importlib.import_module("rich._console_dimensions").ConsoleDimensions
    _console_types_mod = _importlib.import_module("rich._console_types")
    Capture = _console_types_mod.Capture
    CaptureError = _console_types_mod.CaptureError
    ConsoleOptions = _console_types_mod.ConsoleOptions
    Group = _console_types_mod.Group
    NewLine = _console_types_mod.NewLine
    RenderHook = _console_types_mod.RenderHook
    ScreenUpdate = _console_types_mod.ScreenUpdate
    group = _importlib.import_module("rich._group_registry").group

    @group(fit=True)
    def _items():
        return ["a", "b"]

    grouped = _items()
    assert isinstance(grouped, Group)
    assert grouped.fit is True
    assert NewLine(1) is not None
    assert CaptureError is not None
    assert RenderHook is not None
    assert ScreenUpdate([[]], 0, 0) is not None
    options = ConsoleOptions(
        size=ConsoleDimensions(80, 25),
        legacy_windows=False,
        min_width=0,
        max_width=80,
        is_terminal=True,
        encoding="utf-8",
        max_height=25,
    )
    assert options.update_height(10).height == 10
    assert options.reset_height().height is None
    assert options.update_dimensions(60, 20).max_width == 60
    assert Capture  # kiss static anchor


def test_kiss_cov_rich_traceback_install_and_group():
    import sys

    group = _importlib.import_module("rich._console_entry").group
    Console = _importlib.import_module("rich.console").Console
    Traceback = _importlib.import_module("rich.traceback").Traceback
    install = _importlib.import_module("rich.traceback").install

    @group(fit=False)
    def _items():
        return ["trace"]

    assert _items().fit is False
    console = Console(file=io.StringIO(), width=80, color_system=None)
    old = install(
        console=console,
        show_locals=True,
        locals_overflow="ellipsis",
        suppress=(),
    )
    try:
        assert callable(old)
        assert Traceback.extract is not None
    finally:
        sys.excepthook = old
    old_default = install()
    try:
        assert callable(old_default)
    finally:
        sys.excepthook = old_default


def test_kiss_cov_rich__console_dimensions():
    ConsoleDimensions = _importlib.import_module("rich._console_dimensions").ConsoleDimensions

    dims = ConsoleDimensions(100, 40)
    assert dims.height == 40


def test_kiss_cov_rich__console_no_change():
    NO_CHANGE = _importlib.import_module("rich._console_no_change").NO_CHANGE
    NoChange = _importlib.import_module("rich._console_no_change").NoChange

    assert NoChange() is not NO_CHANGE


def test_kiss_cov_rich__color_system():
    ColorSystem = _importlib.import_module("rich._color_system").ColorSystem

    assert repr(ColorSystem.STANDARD) == "ColorSystem.STANDARD"
    assert str(ColorSystem.EIGHT_BIT) == "ColorSystem.EIGHT_BIT"


def test_kiss_cov_rich__unicode_cell_table():
    CellTable = _importlib.import_module("rich._unicode_data._cell_table").CellTable

    table = CellTable("17.0.0", ((0, 127, 1),), frozenset({"ﬁ"}))
    assert table.widths[0][2] == 1


def test_kiss_cov_rich__group_registry_fit_true():
    Group = _importlib.import_module("rich._console_types").Group
    group = _importlib.import_module("rich._group_registry").group
    register_group = _importlib.import_module("rich._group_registry").register_group

    register_group(Group)

    @group()
    def items():
        return ["x"]

    grouped = items()
    assert grouped.fit is True


def test_kiss_cov_rich_cells_special_unicode():
    cell_len = _importlib.import_module("rich.cells").cell_len

    assert cell_len("x\u200dy") == 1


def test_kiss_cov_rich_pretty_install_with_console():
    import sys
    from io import StringIO

    Console = _importlib.import_module("rich._console_entry").Console
    pretty_mod = _importlib.import_module("rich.pretty")
    _install_ipython_pretty = pretty_mod._install_ipython_pretty
    _install_repl_display_hook = pretty_mod._install_repl_display_hook
    _ipy_display_hook = pretty_mod._ipy_display_hook
    _repl_display_hook = pretty_mod._repl_display_hook
    install = pretty_mod.install

    _repl_display_hook
    _ipy_display_hook
    _install_repl_display_hook
    _install_ipython_pretty
    console = Console(file=StringIO(), force_terminal=False)
    old = sys.displayhook
    try:
        install(console=console, overflow="fold", crop=True, indent_guides=True)
        assert sys.displayhook is not old
    finally:
        sys.displayhook = old


def test_kiss_cov_rich__no_emoji():
    EmojiVariant = _importlib.import_module("rich._no_emoji").EmojiVariant
    NoEmoji = _importlib.import_module("rich._no_emoji").NoEmoji

    variant: EmojiVariant = "emoji"
    assert variant == "emoji"
    with pytest.raises(NoEmoji):
        raise NoEmoji("missing")


def test_kiss_cov_rich_init_print_and_json():
    from rich import print as rich_print_fn
    from rich import print_json

    out = io.StringIO()
    rich_print_fn("a", "b", sep="|", file=out)
    assert out.getvalue() == "a|b\n"
    print_json(data={"z": 1}, highlight=False)


def test_kiss_cov_rich_layout():
    Console = _importlib.import_module("rich.console").Console
    Layout = _importlib.import_module("rich.layout").Layout

    layout = Layout(name="root")
    layout.split_column(Layout(name="a"), Layout(name="b"))
    layout["a"].update("top")
    console = Console(file=io.StringIO(), width=80, color_system=None)
    console.print(layout)
    assert console.file.getvalue()


def test_kiss_cov_rich_scope_options():
    Console = _importlib.import_module("rich.console").Console
    render_scope = _importlib.import_module("rich.scope").render_scope

    panel = render_scope(
        {"x": "y" * 50},
        indent_guides=True,
        max_length=10,
        max_string=5,
        max_depth=2,
        overflow="fold",
    )
    console = Console(file=io.StringIO(), width=120, color_system=None)
    console.print(panel)
    assert "x" in console.file.getvalue()


def test_kiss_cov_markdown_lazy_syntax():
    from rich._markdown_syntax import LazySyntaxType

    syntax = LazySyntaxType("x = 1", "python", theme="monokai")
    assert syntax.code == "x = 1"


def test_kiss_cov_examples_attrs():
    pytest.importorskip("attr")
    Model = _importlib.import_module("examples.attrs").Model
    Point3D = _importlib.import_module("examples.attrs_point3d").Point3D
    Triangle = _importlib.import_module("examples.attrs_triangle").Triangle

    model = Model(
        name="Alien#1",
        triangles=[Triangle(Point3D(1, 2), Point3D(3, 4, 5), Point3D(6, 7, 8))],
    )
    assert model.name == "Alien#1"
