"""Tests for the highlighter classes."""
import json
from typing import List

import pytest

from rich._highlight_bridge import (
    align_panel_border_label,
    configure,
    configure_markup,
    configure_panel,
    copy_text,
    escape_markup,
    is_text,
    make_span,
    invoke_markup_render,
    normalize_panel_label,
    text_create,
    text_from_str,
)
from rich.console import Console
from rich.panel import Panel
from rich.highlighter import (
    ISO8601Highlighter,
    JSONHighlighter,
    NullHighlighter,
    ReprHighlighter,
)
from rich.text import Span, Text


def test_highlight_bridge():
    configure(Text, Text.copy, Span)
    created = text_from_str("hello")
    assert created.plain == "hello"
    copied = copy_text(Text("x"))
    assert copied.plain == "x"
    assert is_text(Text("y"))
    assert not is_text("z")
    styled = text_create("plain", style="bold")
    assert styled.plain == "plain"
    span = make_span(0, 3, "bold")
    assert span == Span(0, 3, "bold")


def test_markup_bridge():
    import rich.markup as markup_module

    configure_markup(markup_module.render, markup_module.escape)
    rendered = invoke_markup_render("[bold]hi[/bold]")
    assert rendered.plain == "hi"
    assert markup_module.render("no tags", style="dim").plain == "no tags"
    assert escape_markup("plain") == "plain"
    assert Text.from_markup("[green]ok[/green]").plain == "ok"
    assert Text("x", style="bold").markup == "[bold]x[/bold]"


def test_panel_bridge():
    import rich.text as text_module

    configure_panel(
        text_module._normalize_panel_label,
        text_module._align_panel_border_label,
    )
    label = normalize_panel_label("hello")
    assert label.plain == " hello "
    console = Console(width=40, record=True)
    aligned = align_panel_border_label(console, label, 10, "center", "-", "bold")
    assert aligned.plain
    panel = Panel("body", title="Title")
    console.print(panel)
    assert "Title" in console.export_text()


def test_panel_bridge_unconfigured():
    import rich._highlight_bridge as bridge

    saved = (
        bridge._normalize_panel_label,
        bridge._align_panel_border_label,
    )
    bridge._normalize_panel_label = None
    bridge._align_panel_border_label = None
    try:
        with pytest.raises(RuntimeError, match="rich.text has not registered"):
            normalize_panel_label("x")
        with pytest.raises(RuntimeError, match="rich.text has not registered"):
            align_panel_border_label(Console(), Text("x"), 5, "left", "-", "bold")
    finally:
        bridge._normalize_panel_label, bridge._align_panel_border_label = saved


def test_markup_bridge_unconfigured():
    import rich._highlight_bridge as bridge

    saved = (
        bridge._render_markup,
        bridge._escape_markup,
    )
    bridge._render_markup = None
    bridge._escape_markup = None
    try:
        with pytest.raises(RuntimeError, match="rich.markup has not registered"):
            invoke_markup_render("plain")
        with pytest.raises(RuntimeError, match="rich.markup has not registered"):
            escape_markup("plain")
    finally:
        bridge._render_markup, bridge._escape_markup = saved


def test_wrong_type():
    highlighter = NullHighlighter()
    with pytest.raises(TypeError):
        highlighter([])


highlight_tests = [
    ("", []),
    (" ", []),
    (
        "<foo>",
        [
            Span(0, 1, "repr.tag_start"),
            Span(1, 4, "repr.tag_name"),
            Span(4, 5, "repr.tag_end"),
        ],
    ),
    (
        "<foo: 23>",
        [
            Span(0, 1, "repr.tag_start"),
            Span(1, 5, "repr.tag_name"),
            Span(5, 8, "repr.tag_contents"),
            Span(8, 9, "repr.tag_end"),
            Span(6, 8, "repr.number"),
        ],
    ),
    (
        "<foo: <bar: 23>>",
        [
            Span(0, 1, "repr.tag_start"),
            Span(1, 5, "repr.tag_name"),
            Span(5, 15, "repr.tag_contents"),
            Span(15, 16, "repr.tag_end"),
            Span(12, 14, "repr.number"),
        ],
    ),
    (
        "False True None",
        [
            Span(0, 5, "repr.bool_false"),
            Span(6, 10, "repr.bool_true"),
            Span(11, 15, "repr.none"),
        ],
    ),
    ("foo=bar", [Span(0, 3, "repr.attrib_name"), Span(4, 7, "repr.attrib_value")]),
    (
        'foo="bar"',
        [
            Span(0, 3, "repr.attrib_name"),
            Span(4, 9, "repr.attrib_value"),
            Span(4, 9, "repr.str"),
        ],
    ),
    (
        "<Permission.WRITE|READ: 3>",
        [
            Span(0, 1, "repr.tag_start"),
            Span(1, 23, "repr.tag_name"),
            Span(23, 25, "repr.tag_contents"),
            Span(25, 26, "repr.tag_end"),
            Span(24, 25, "repr.number"),
        ],
    ),
    ("( )", [Span(0, 1, "repr.brace"), Span(2, 3, "repr.brace")]),
    ("[ ]", [Span(0, 1, "repr.brace"), Span(2, 3, "repr.brace")]),
    ("{ }", [Span(0, 1, "repr.brace"), Span(2, 3, "repr.brace")]),
    (" 1 ", [Span(1, 2, "repr.number")]),
    (" 1.2 ", [Span(1, 4, "repr.number")]),
    (" 0xff ", [Span(1, 5, "repr.number")]),
    (" 1e10 ", [Span(1, 5, "repr.number")]),
    (" 1j ", [Span(1, 3, "repr.number_complex")]),
    (" 3.14j ", [Span(1, 6, "repr.number_complex")]),
    (
        " (3.14+2.06j) ",
        [
            Span(1, 2, "repr.brace"),
            Span(12, 13, "repr.brace"),
            Span(2, 12, "repr.number_complex"),
        ],
    ),
    (
        " (3+2j) ",
        [
            Span(1, 2, "repr.brace"),
            Span(6, 7, "repr.brace"),
            Span(2, 6, "repr.number_complex"),
        ],
    ),
    (
        " (123456.4321-1234.5678j) ",
        [
            Span(1, 2, "repr.brace"),
            Span(24, 25, "repr.brace"),
            Span(2, 24, "repr.number_complex"),
        ],
    ),
    (
        " (-123123-2.1312342342423422e+25j) ",
        [
            Span(1, 2, "repr.brace"),
            Span(33, 34, "repr.brace"),
            Span(2, 33, "repr.number_complex"),
        ],
    ),
    (" /foo ", [Span(1, 2, "repr.path"), Span(2, 5, "repr.filename")]),
    (" /foo/bar.html ", [Span(1, 6, "repr.path"), Span(6, 14, "repr.filename")]),
    ("01-23-45-67-89-AB", [Span(0, 17, "repr.eui48")]),  # 6x2 hyphen
    ("01-23-45-FF-FE-67-89-AB", [Span(0, 23, "repr.eui64")]),  # 8x2 hyphen
    ("01:23:45:67:89:AB", [Span(0, 17, "repr.ipv6")]),  # 6x2 colon
    ("01:23:45:FF:FE:67:89:AB", [Span(0, 23, "repr.ipv6")]),  # 8x2 colon
    ("0123.4567.89AB", [Span(0, 14, "repr.eui48")]),  # 3x4 dot
    ("0123.45FF.FE67.89AB", [Span(0, 19, "repr.eui64")]),  # 4x4 dot
    ("ed-ed-ed-ed-ed-ed", [Span(0, 17, "repr.eui48")]),  # lowercase
    ("ED-ED-ED-ED-ED-ED", [Span(0, 17, "repr.eui48")]),  # uppercase
    ("Ed-Ed-Ed-Ed-Ed-Ed", [Span(0, 17, "repr.eui48")]),  # mixed case
    ("0-00-1-01-2-02", [Span(0, 14, "repr.eui48")]),  # dropped zero
    (" https://example.org ", [Span(1, 20, "repr.url")]),
    (" http://example.org ", [Span(1, 19, "repr.url")]),
    (" http://example.org/index.html ", [Span(1, 30, "repr.url")]),
    (" http://example.org/index.html#anchor ", [Span(1, 37, "repr.url")]),
    ("https://www.youtube.com/@LinusTechTips", [Span(0, 38, "repr.url")]),
    (
        " http://example.org/index.html?param1=value1 ",
        [
            Span(31, 37, "repr.attrib_name"),
            Span(38, 44, "repr.attrib_value"),
            Span(1, 44, "repr.url"),
        ],
    ),
    (" http://example.org/~folder ", [Span(1, 27, "repr.url")]),
    ("No place like 127.0.0.1", [Span(14, 23, "repr.ipv4")]),
    ("''", [Span(0, 2, "repr.str")]),
    ("'hello'", [Span(0, 7, "repr.str")]),
    ("'''hello'''", [Span(0, 11, "repr.str")]),
    ('""', [Span(0, 2, "repr.str")]),
    ('"hello"', [Span(0, 7, "repr.str")]),
    ('"""hello"""', [Span(0, 11, "repr.str")]),
    ("\\'foo'", []),
    ("it's no 'string'", [Span(8, 16, "repr.str")]),
    ("78351748-9b32-4e08-ad3e-7e9ff124d541", [Span(0, 36, "repr.uuid")]),
]


@pytest.mark.parametrize("test, spans", highlight_tests)
def test_highlight_regex(test: str, spans: List[Span]):
    """Tests for the regular expressions used in ReprHighlighter."""
    text = Text(test)
    highlighter = ReprHighlighter()
    highlighter.highlight(text)
    print(text.spans)
    assert text.spans == spans


def test_highlight_json_with_indent():
    json_string = json.dumps({"name": "apple", "count": 1}, indent=4)
    text = Text(json_string)
    highlighter = JSONHighlighter()
    highlighter.highlight(text)
    assert text.spans == [
        Span(0, 1, "json.brace"),
        Span(6, 12, "json.str"),
        Span(14, 21, "json.str"),
        Span(27, 34, "json.str"),
        Span(36, 37, "json.number"),
        Span(38, 39, "json.brace"),
        Span(6, 12, "json.key"),
        Span(27, 34, "json.key"),
    ]


def test_highlight_json_string_only():
    json_string = '"abc"'
    text = Text(json_string)
    highlighter = JSONHighlighter()
    highlighter.highlight(text)
    assert text.spans == [Span(0, 5, "json.str")]


def test_highlight_json_empty_string_only():
    json_string = '""'
    text = Text(json_string)
    highlighter = JSONHighlighter()
    highlighter.highlight(text)
    assert text.spans == [Span(0, 2, "json.str")]


def test_highlight_json_no_indent():
    json_string = json.dumps({"name": "apple", "count": 1}, indent=None)
    text = Text(json_string)
    highlighter = JSONHighlighter()
    highlighter.highlight(text)
    assert text.spans == [
        Span(0, 1, "json.brace"),
        Span(1, 7, "json.str"),
        Span(9, 16, "json.str"),
        Span(18, 25, "json.str"),
        Span(27, 28, "json.number"),
        Span(28, 29, "json.brace"),
        Span(1, 7, "json.key"),
        Span(18, 25, "json.key"),
    ]


iso8601_highlight_tests = [
    ("2008-08", [Span(0, 4, "iso8601.year"), Span(5, 7, "iso8601.month")]),
    (
        "2008-08-30",
        [
            Span(0, 10, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 7, "iso8601.month"),
            Span(8, 10, "iso8601.day"),
        ],
    ),
    (
        "20080830",
        [
            Span(0, 8, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(4, 6, "iso8601.month"),
            Span(6, 8, "iso8601.day"),
        ],
    ),
    (
        "2008-243",
        [
            Span(0, 8, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 8, "iso8601.day"),
        ],
    ),
    (
        "2008243",
        [
            Span(0, 7, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(4, 7, "iso8601.day"),
        ],
    ),
    (
        "2008-W35",
        [
            Span(0, 8, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(6, 8, "iso8601.week"),
        ],
    ),
    (
        "2008W35",
        [
            Span(0, 7, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 7, "iso8601.week"),
        ],
    ),
    (
        "2008-W35-6",
        [
            Span(0, 10, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(6, 8, "iso8601.week"),
            Span(9, 10, "iso8601.day"),
        ],
    ),
    (
        "2008W356",
        [
            Span(0, 8, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 7, "iso8601.week"),
            Span(7, 8, "iso8601.day"),
        ],
    ),
    (
        "17:21",
        [
            Span(0, 5, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(3, 5, "iso8601.minute"),
        ],
    ),
    (
        "1721",
        [
            Span(0, 4, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(2, 4, "iso8601.minute"),
        ],
    ),
    (
        "172159",
        [
            Span(0, 6, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(2, 4, "iso8601.minute"),
            Span(4, 6, "iso8601.second"),
        ],
    ),
    ("Z", [Span(0, 1, "iso8601.timezone")]),
    ("+07", [Span(0, 3, "iso8601.timezone")]),
    ("+07:00", [Span(0, 6, "iso8601.timezone")]),
    (
        "17:21:59+07:00",
        [
            Span(0, 8, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(3, 5, "iso8601.minute"),
            Span(6, 8, "iso8601.second"),
            Span(8, 14, "iso8601.timezone"),
        ],
    ),
    (
        "172159+0700",
        [
            Span(0, 6, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(2, 4, "iso8601.minute"),
            Span(4, 6, "iso8601.second"),
            Span(6, 11, "iso8601.timezone"),
        ],
    ),
    (
        "172159+07",
        [
            Span(0, 6, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(2, 4, "iso8601.minute"),
            Span(4, 6, "iso8601.second"),
            Span(6, 9, "iso8601.timezone"),
        ],
    ),
    (
        "2008-08-30 17:21:59",
        [
            Span(0, 10, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(4, 5, "iso8601.hyphen"),
            Span(5, 7, "iso8601.month"),
            Span(8, 10, "iso8601.day"),
            Span(11, 19, "iso8601.time"),
            Span(11, 13, "iso8601.hour"),
            Span(14, 16, "iso8601.minute"),
            Span(17, 19, "iso8601.second"),
        ],
    ),
    (
        "20080830 172159",
        [
            Span(0, 8, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(4, 6, "iso8601.month"),
            Span(6, 8, "iso8601.day"),
            Span(9, 15, "iso8601.time"),
            Span(9, 11, "iso8601.hour"),
            Span(11, 13, "iso8601.minute"),
            Span(13, 15, "iso8601.second"),
        ],
    ),
    (
        "2008-08-30",
        [
            Span(0, 10, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 7, "iso8601.month"),
            Span(8, 10, "iso8601.day"),
        ],
    ),
    (
        "2008-08-30+07:00",
        [
            Span(0, 10, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 7, "iso8601.month"),
            Span(8, 10, "iso8601.day"),
            Span(10, 16, "iso8601.timezone"),
        ],
    ),
    (
        "01:45:36",
        [
            Span(0, 8, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(3, 5, "iso8601.minute"),
            Span(6, 8, "iso8601.second"),
        ],
    ),
    (
        "01:45:36.123+07:00",
        [
            Span(0, 12, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(3, 5, "iso8601.minute"),
            Span(6, 8, "iso8601.second"),
            Span(8, 12, "iso8601.frac"),
            Span(12, 18, "iso8601.timezone"),
        ],
    ),
    (
        "01:45:36.123+07:00",
        [
            Span(0, 12, "iso8601.time"),
            Span(0, 2, "iso8601.hour"),
            Span(3, 5, "iso8601.minute"),
            Span(6, 8, "iso8601.second"),
            Span(8, 12, "iso8601.frac"),
            Span(12, 18, "iso8601.timezone"),
        ],
    ),
    (
        "2008-08-30T01:45:36",
        [
            Span(0, 10, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 7, "iso8601.month"),
            Span(8, 10, "iso8601.day"),
            Span(11, 19, "iso8601.time"),
            Span(11, 13, "iso8601.hour"),
            Span(14, 16, "iso8601.minute"),
            Span(17, 19, "iso8601.second"),
        ],
    ),
    (
        "2008-08-30T01:45:36.123Z",
        [
            Span(0, 10, "iso8601.date"),
            Span(0, 4, "iso8601.year"),
            Span(5, 7, "iso8601.month"),
            Span(8, 10, "iso8601.day"),
            Span(11, 23, "iso8601.time"),
            Span(11, 13, "iso8601.hour"),
            Span(14, 16, "iso8601.minute"),
            Span(17, 19, "iso8601.second"),
            Span(19, 23, "iso8601.ms"),
            Span(23, 24, "iso8601.timezone"),
        ],
    ),
]


@pytest.mark.parametrize("test, spans", iso8601_highlight_tests)
def test_highlight_iso8601_regex(test: str, spans: List[Span]):
    """Tests for the regular expressions used in ISO8601Highlighter."""
    text = Text(test)
    highlighter = ISO8601Highlighter()
    highlighter.highlight(text)
    print(text.spans)
    assert text.spans == spans
