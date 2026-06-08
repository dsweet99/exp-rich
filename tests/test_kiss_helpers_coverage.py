"""Kiss coverage for extracted helper modules."""
from __future__ import annotations

import importlib as _importlib
from types import SimpleNamespace

def test_kiss_cov_ansi_decode_line():
    _mod_rich__ansi_decode_line = _importlib.import_module("rich._ansi_decode_line")
    decode_line_tokens = _mod_rich__ansi_decode_line.decode_line_tokens
    _mod_rich_ansi = _importlib.import_module("rich.ansi")
    _ansi_tokenize = _mod_rich_ansi._ansi_tokenize
    _mod_rich_color = _importlib.import_module("rich.color")
    Color = _mod_rich_color.Color
    _mod_rich_style = _importlib.import_module("rich.style")
    Style = _mod_rich_style.Style
    _mod_rich_text = _importlib.import_module("rich.text")
    Text = _mod_rich_text.Text

    text, _style = decode_line_tokens(
        "hello", Style.null(), Style, Color, Text, _ansi_tokenize("hello")
    )
    assert text.plain == "hello"


def test_kiss_cov_lines_justify():
    _mod_rich__lines_justify = _importlib.import_module("rich._lines_justify")
    (
    justify_center,
    justify_full,
    justify_left,
    justify_right,
) = (
    _mod_rich__lines_justify.justify_center,
    _mod_rich__lines_justify.justify_full,
    _mod_rich__lines_justify.justify_left,
    _mod_rich__lines_justify.justify_right,
)
    _mod_rich__console_entry = _importlib.import_module("rich._console_entry")
    Console = _mod_rich__console_entry.Console
    _mod_rich_text = _importlib.import_module("rich.text")
    Text = _mod_rich_text.Text

    console = Console()
    lines = [Text("foo")]
    justify_left(lines, 10, "fold")
    justify_center(lines, 10, "fold")
    justify_right(lines, 10, "fold")
    justify_full(lines, console, 10, Text)
    assert len(lines) == 1


def test_kiss_cov_json_highlight_keys():
    _mod_rich__json_highlight = _importlib.import_module("rich._json_highlight")
    highlight_json_keys = _mod_rich__json_highlight.highlight_json_keys
    _mod_rich__highlight_kernel = _importlib.import_module("rich._highlight_kernel")
    span_class = _mod_rich__highlight_kernel.span_class
    _mod_rich_text = _importlib.import_module("rich.text")
    Text = _mod_rich_text.Text

    json_str = r'(?P<str>"[^"]*")'
    text = Text('"key" : "value"')
    highlight_json_keys(text, json_str, frozenset({" "}), span_class())


def test_kiss_cov_text_getitem():
    _mod_rich_text = _importlib.import_module("rich.text")
    Text = _mod_rich_text.Text

    text = Text("abc", style="bold")
    assert text[1].plain == "b"


def test_kiss_cov_combine_regex():
    _mod_rich__highlighter_exports = _importlib.import_module("rich._highlighter_exports")
    combine_regex = _mod_rich__highlighter_exports.combine_regex

    assert combine_regex("a", "b") == "a|b"
    assert combine_regex("only") == "only"


def test_kiss_cov_flush_console_buffer():
    from unittest.mock import MagicMock

    _mod_rich__console_buffer_io = _importlib.import_module("rich._console_buffer_io")

    flush_console_buffer = _mod_rich__console_buffer_io.flush_console_buffer
    _mod_rich_segment = _importlib.import_module("rich.segment")
    Segment = _mod_rich_segment.Segment

    console = MagicMock(is_jupyter=False, legacy_windows=False, file=MagicMock())
    buffer = [Segment("x")]
    flush_console_buffer(
        console,
        buffer,
        lambda buf: "x",
        lambda f: None,
        Segment,
        windows=False,
        is_jupyter=False,
    )
    assert buffer == []


def test_kiss_cov_console_init_helpers():
    from unittest.mock import MagicMock

    _mod_rich__console_init = _importlib.import_module("rich._console_init")

    (
    init_console_state,
    resolve_env_dimensions,
    resolve_force_interactive,
    resolve_jupyter_dimensions,
) = (
    _mod_rich__console_init.init_console_state,
    _mod_rich__console_init.resolve_env_dimensions,
    _mod_rich__console_init.resolve_force_interactive,
    _mod_rich__console_init.resolve_jupyter_dimensions,
)

    is_jupyter, width, height = resolve_jupyter_dimensions(
        {"JUPYTER_COLUMNS": "100", "JUPYTER_LINES": "50"},
        force_jupyter=True,
        is_jupyter_fn=lambda: False,
        width=None,
        height=None,
        default_columns=80,
        default_lines=24,
    )
    assert is_jupyter is True
    assert width == 100
    assert height == 50

    width, height = resolve_env_dimensions(
        {"COLUMNS": "120", "LINES": "40"},
        legacy_windows=False,
        width=None,
        height=None,
    )
    assert width == 120
    assert height == 40

    assert resolve_force_interactive({"TTY_INTERACTIVE": "1"}, None) is True
    assert resolve_force_interactive({"TTY_INTERACTIVE": "0"}, None) is False

    console = MagicMock()
    console.is_terminal = True
    console.is_dumb_terminal = False
    import rich._log_render  # noqa: F401 — register LogRender

    init_console_state(
        console,
        environ={"NO_COLOR": ""},
        tab_size=8,
        record=False,
        markup=True,
        emoji=True,
        emoji_variant=None,
        highlight=True,
        soft_wrap=False,
        width=80,
        height=24,
        force_terminal=None,
        file=None,
        quiet=False,
        stderr=False,
        color_system_name="auto",
        color_systems={"auto": "auto"},
        detect_color_system=lambda: None,
        ensure_render_factories=lambda: None,
        log_time=True,
        log_path=True,
        log_time_format="[%X]",
        highlighter=None,
        safe_box=True,
        get_datetime=None,
        get_time=None,
        no_color=None,
        force_interactive=None,
        theme=None,
    )
    assert console.is_interactive is True


def test_kiss_cov_pretty_ipython_formatter():
    from unittest.mock import MagicMock

    _mod_rich__pretty_ipython = _importlib.import_module("rich._pretty_ipython")

    register_ipython_formatter = _mod_rich__pretty_ipython.register_ipython_formatter

    ip = MagicMock()
    formatters: dict = {}
    ip.display_formatter.formatters = formatters
    hook = MagicMock(return_value="rich")
    register_ipython_formatter(
        ip,
        hook,
        console=MagicMock(),
        overflow="fold",
        indent_guides=False,
        max_length=None,
        max_string=None,
        max_depth=None,
        expand_all=False,
    )
    formatter = formatters["text/plain"]
    assert formatter("x") == "rich"
    hook.assert_called_once()


def _text_helper_bindings() -> SimpleNamespace:
    _mod_rich__console_entry = _importlib.import_module("rich._console_entry")
    _mod_rich_text = _importlib.import_module("rich.text")
    _mod_rich_segment = _importlib.import_module("rich.segment")
    _mod_rich_style = _importlib.import_module("rich.style")
    return SimpleNamespace(
        Console=_mod_rich__console_entry.Console,
        Text=_mod_rich_text.Text,
        append_string=_mod_rich_text.append_string,
        append_text_instance=_mod_rich_text.append_text_instance,
        detect_indentation=_mod_rich_text.detect_indentation,
        divide_text_at_offsets=_mod_rich_text.divide_text_at_offsets,
        expand_tabs_in_text=_mod_rich_text.expand_tabs_in_text,
        render_text_segments=_mod_rich_text.render_text_segments,
        truncate_text=_mod_rich_text.truncate_text,
        with_indent_guides=_mod_rich_text.with_indent_guides,
        wrap_line=_mod_rich_text.wrap_line,
        wrap_text=_mod_rich_text.wrap_text,
        Segment=_mod_rich_segment.Segment,
        Style=_mod_rich_style.Style,
    )


def test_kiss_cov_text_mutations() -> None:
    bindings = _text_helper_bindings()
    Text = bindings.Text
    append_string = bindings.append_string
    append_text_instance = bindings.append_text_instance
    detect_indentation = bindings.detect_indentation
    expand_tabs_in_text = bindings.expand_tabs_in_text
    truncate_text = bindings.truncate_text
    with_indent_guides = bindings.with_indent_guides

    text = Text("hello\tworld", style="bold")
    expand_tabs_in_text(text, 4, Text)
    assert "\t" not in text.plain

    append_string(text, "!", "red")
    append_text_instance(text, Text("x", style="italic"))

    truncate_text(text, 20, "fold", pad=True)

    indented = Text("  line\n    nested")
    assert detect_indentation(indented) >= 1
    guided = with_indent_guides(indented, 2, "│", "dim", Text)
    assert guided.plain


def test_kiss_cov_text_divide_at_offsets() -> None:
    bindings = _text_helper_bindings()
    Text = bindings.Text
    divide_text_at_offsets = bindings.divide_text_at_offsets
    _mod_rich__text_span = _importlib.import_module("rich._text_span")
    Span = _mod_rich__text_span.Span

    divided = divide_text_at_offsets(Text("abc\ndef"), [3], Text)
    assert len(divided) == 2
    spanned_divided = divide_text_at_offsets(
        Text("abcdef", spans=[Span(0, 3, "bold")]), [3], Text
    )
    assert len(spanned_divided) == 2


def test_kiss_cov_text_render_and_wrap() -> None:
    bindings = _text_helper_bindings()
    Console = bindings.Console
    Text = bindings.Text
    render_text_segments = bindings.render_text_segments
    with_indent_guides = bindings.with_indent_guides
    wrap_line = bindings.wrap_line
    wrap_text = bindings.wrap_text
    Segment = bindings.Segment
    Style = bindings.Style

    console = Console(file=__import__("io").StringIO(), width=80, color_system=None)
    segments = list(render_text_segments(Text("hi", style="bold"), console, "", Segment, Style))
    assert segments

    wrapped = wrap_line(Text("hello world"), console, 5, "left", "fold", 8, False, Text)
    assert len(wrapped) >= 1
    wrapped_lines = wrap_text(Text("hello world"), console, 10, "left", "fold", 8, False, Text)
    assert len(wrapped_lines) >= 1

    auto = with_indent_guides(
        Text(
            """\
for a in range(10):
    print(a)

foo = [
    1,
    {
        2
    }
]

"""
        ),
        None,
        "│",
        "dim green",
        Text,
    )
    expected = "for a in range(10):\n│   print(a)\n\nfoo = [\n│   1,\n│   {\n│   │   2\n│   }\n]\n\n"
    assert auto.plain == expected


def test_kiss_cov_box_row_helpers():
    _mod_rich__box_row = _importlib.import_module("rich._box_row")
    box_row_edges = _mod_rich__box_row.box_row_edges
    build_box_row = _mod_rich__box_row.build_box_row
    _mod_rich_box = _importlib.import_module("rich.box")
    SQUARE = _mod_rich_box.SQUARE

    left, horizontal, cross, right = box_row_edges(SQUARE, "head")
    assert left == SQUARE.head_row_left
    row = build_box_row(left, horizontal, cross, right, [2, 3], edge=True)
    assert SQUARE.get_row([2, 3], level="head") == row


def test_kiss_cov_layout_find():
    import rich.highlighter  # noqa: F401 — register highlighter for layout import
    _mod_rich__layout_find = _importlib.import_module("rich._layout_find")
    find_layout_by_name = _mod_rich__layout_find.find_layout_by_name
    _mod_rich_layout = _importlib.import_module("rich.layout")
    Layout = _mod_rich_layout.Layout

    root = Layout(name="root")
    child = Layout(name="child")
    root.split(child)
    assert find_layout_by_name(root, "child") is child
    assert find_layout_by_name(root, "missing") is None


def test_kiss_cov_log_render_rows():
    from datetime import datetime
    from io import StringIO

    _mod_rich__log_render = _importlib.import_module("rich._log_render")

    (
    LogRender,
    append_log_path,
    append_log_time,
    build_log_table,
    format_log_time_display,
) = (
    _mod_rich__log_render.LogRender,
    _mod_rich__log_render.append_log_path,
    _mod_rich__log_render.append_log_time,
    _mod_rich__log_render.build_log_table,
    _mod_rich__log_render.format_log_time_display,
)
    _mod_rich__render_factory = _importlib.import_module("rich._render_factory")
    renderables = _mod_rich__render_factory.renderables
    table_grid = _mod_rich__render_factory.table_grid
    _mod_rich__console_entry = _importlib.import_module("rich._console_entry")
    Console = _mod_rich__console_entry.Console
    _mod_rich_text = _importlib.import_module("rich.text")
    Text = _mod_rich_text.Text

    display = format_log_time_display(datetime(2020, 1, 1), "[%Y]", Text)
    assert "2020" in display.plain

    row: list = []
    last = append_log_time(
        row,
        log_time=datetime(2020, 1, 1),
        time_format="[%Y]",
        omit_repeated_times=False,
        last_time=None,
        text_cls=Text,
    )
    assert last is not None
    append_log_path(row, path="/tmp/x", line_no=1, link_path="/tmp/x", text_cls=Text)
    assert len(row) == 2

    console = Console(file=StringIO(), width=80, color_system=None)
    renderer = LogRender(show_time=True, show_path=True)
    table = build_log_table(
        renderer,
        console,
        [Text("msg")],
        log_time=datetime(2020, 1, 1),
        time_format="[%Y]",
        level=Text("INFO"),
        path="/tmp/x",
        line_no=3,
        link_path="/tmp/x",
        table_grid_fn=table_grid,
        make_renderables_fn=renderables,
        text_cls=Text,
    )
    assert table.row_count == 1


def test_kiss_cov_style_format_helpers():
    from rich import errors
    _mod_rich_color = _importlib.import_module("rich.color")
    Color = _mod_rich_color.Color
    _mod_rich_color = _importlib.import_module("rich.color")
    blend_rgb = _mod_rich_color.blend_rgb
    _mod_rich_style = _importlib.import_module("rich.style")
    (
    Style,
    build_html_style,
    build_style_definition,
    make_ansi_codes,
    parse_style_words,
) = (
    _mod_rich_style.Style,
    _mod_rich_style.build_html_style,
    _mod_rich_style.build_style_definition,
    _mod_rich_style.make_ansi_codes,
    _mod_rich_style.parse_style_words,
)
    _mod_rich_terminal_theme = _importlib.import_module("rich.terminal_theme")
    DEFAULT_TERMINAL_THEME = _mod_rich_terminal_theme.DEFAULT_TERMINAL_THEME

    style = Style(bold=True, color="red")
    definition = build_style_definition(style)
    assert "bold" in definition
    assert Style.parse(definition).bold is True

    ansi = make_ansi_codes(style, Color.parse("red").system)
    assert isinstance(ansi, str)

    parsed = parse_style_words(
        Style,
        iter("bold red on white".split()),
        errors_module=errors,
        color_parse=Color.parse,
    )
    assert parsed.bold is True

    css = build_html_style(style, DEFAULT_TERMINAL_THEME, blend_rgb, Color)
    assert "color:" in css


def test_kiss_cov_traceback_syntax_lines():
    _mod_rich__traceback_syntax_lines = _importlib.import_module("rich._traceback_syntax_lines")
    iter_syntax_lines = _mod_rich__traceback_syntax_lines.iter_syntax_lines
    syntax_line_span = _mod_rich__traceback_syntax_lines.syntax_line_span

    assert syntax_line_span(True, False, 1, 2, 5) == (1, 2, -1)
    assert syntax_line_span(False, True, 3, 2, 5) == (3, 0, 5)
    assert syntax_line_span(False, False, 2, 2, 5) == (2, 0, -1)

    single = list(iter_syntax_lines((1, 2), (1, 8)))
    assert single == [(1, 2, 8)]

    multi = list(iter_syntax_lines((1, 2), (3, 5)))
    assert multi[0] == (1, 2, -1)
    assert multi[-1] == (3, 0, 5)


def test_kiss_cov_console_log_emit():
    import io

    _mod_rich__console_entry = _importlib.import_module("rich._console_entry")

    Console = _mod_rich__console_entry.Console

    console = Console(file=io.StringIO(), width=80, color_system=None)
    console.log("hello")
    assert "hello" in console.file.getvalue()


def test_kiss_cov_syntax_highlight_helpers():
    _mod_rich__syntax_highlight = _importlib.import_module("rich._syntax_highlight")
    append_highlighted_code = _mod_rich__syntax_highlight.append_highlighted_code
    _mod_rich__syntax_stylized = _importlib.import_module("rich._syntax_stylized")
    (
    apply_stylized_ranges,
    get_code_index_for_syntax_position,
) = (
    _mod_rich__syntax_stylized.apply_stylized_ranges,
    _mod_rich__syntax_stylized.get_code_index_for_syntax_position,
)
    _mod_rich_syntax = _importlib.import_module("rich.syntax")
    Syntax = _mod_rich_syntax.Syntax
    _SyntaxHighlightRange = _mod_rich_syntax._SyntaxHighlightRange
    _mod_rich_text = _importlib.import_module("rich.text")
    Text = _mod_rich_text.Text

    syntax = Syntax("x = 1\n", "python", theme="ansi_dark")
    text = Text()
    append_highlighted_code(syntax, text, "x = 1\n", None)
    assert "x" in text.plain

    text2 = Text("line\n")
    apply_stylized_ranges(
        text2,
        [_SyntaxHighlightRange("bold", (1, 0), (1, 4))],
    )
    assert text2.plain == "line\n"
    assert get_code_index_for_syntax_position([0, 5, 6], (1, 2)) == 2


def test_kiss_cov_traceback_init_helpers():
    import os
    from types import ModuleType

    _mod_rich__traceback_init = _importlib.import_module("rich._traceback_init")

    normalize_suppress_paths = _mod_rich__traceback_init.normalize_suppress_paths

    resolve_trace_or_raise = _mod_rich__traceback_init.resolve_trace_or_raise

    paths = normalize_suppress_paths([os.path.curdir])
    assert paths

    mod = ModuleType("m")
    mod.__file__ = __file__
    paths = normalize_suppress_paths([mod])
    assert paths[0].endswith("tests")

    assert resolve_trace_or_raise({"frames": []}, extract=lambda *a, **k: {"ok": True}, show_locals=False) == {"frames": []}


def test_kiss_cov_cells_len_module():
    _mod_rich__cells_len = _importlib.import_module("rich._cells_len")
    cached_cell_len = _mod_rich__cells_len.cached_cell_len
    cell_len = _mod_rich__cells_len.cell_len

    assert cell_len("hello") == 5
    assert cached_cell_len("hello") == 5


def test_kiss_cov_cell_len_long_path():
    _mod_rich__cells_len = _importlib.import_module("rich._cells_len")
    cell_len = _mod_rich__cells_len.cell_len

    assert cell_len("a" * 512) == 512
    assert cell_len("a" * 1000) == 1000


def test_kiss_cov_cells_cell_len_direct():
    _mod_rich_cells = _importlib.import_module("rich.cells")
    cell_len = _mod_rich_cells.cell_len
    chop_cells = _mod_rich_cells.chop_cells
    set_cell_size = _mod_rich_cells.set_cell_size
    split_text = _mod_rich_cells.split_text

    assert cell_len("a" * 513) == 513
    assert cell_len("💩" * 300) == 600
    left, right = split_text("💩ab", 2)
    assert len(left) >= 1
    assert chop_cells("💩a💩", width=2)
    _mod_rich_cells = _importlib.import_module("rich.cells")
    measure = _mod_rich_cells.cell_len

    assert measure(set_cell_size("💩", 3)) == 3


def test_kiss_cov_deferred_type_and_module() -> None:
    _deferred_type = _importlib.import_module("rich._deferred_type")
    _deferred_module = _importlib.import_module("rich._deferred_module")
    DeferredType = _deferred_type.DeferredType
    DeferredModule = _deferred_module.DeferredModule

    class _Box:
        tag = "box"

        def __init__(self, value: int) -> None:
            self.value = value

    box = DeferredType(lambda: _Box)
    assert box.tag == "box"
    assert box(7).value == 7

    color_mod = DeferredModule("._color_system", "rich")
    assert color_mod.ColorSystem.STANDARD.name == "STANDARD"
