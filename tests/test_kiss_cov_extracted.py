"""Tests for exec-erased render helpers."""
from __future__ import annotations

import io


def test_kiss_cov_segment_divide():
    from rich._segment_divide import divide_segments
    from rich.segment import Segment

    segments = [Segment("hello world")]
    parts = list(divide_segments(Segment, segments, [5, 11]))
    assert len(parts) >= 2
    assert "".join(part[0].text for part in parts if part) == "hello world"


def test_kiss_cov_segment_line_ops():
    from rich._console_entry import Console
    from rich._segment_line_ops import adjust_line_segments, crop_newline_segment
    from rich.segment import Segment

    cls = Segment
    line = [Segment("hi")]
    adjusted = adjust_line_segments(cls, line, 10, None, True)
    assert sum(segment.cell_length for segment in adjusted) == 10

    console = Console(file=io.StringIO(), width=40, color_system=None)
    newline_line: list[Segment] = []
    cropped = list(
        crop_newline_segment(
            cls,
            Segment("a\nb"),
            newline_line,
            newline_line.append,
            cls.adjust_line_length,
            5,
            None,
            True,
            True,
            cls("\n"),
        )
    )
    assert cropped
    assert console.render_str("x")


def test_kiss_cov_panel_console():
    from rich._console_entry import Console
    from rich._panel_console import render_panel
    from rich.panel import Panel

    panel = Panel("hello", title="Title", padding=0)
    console = Console(file=io.StringIO(), width=40, color_system=None)
    output = list(render_panel(panel, console, console.options))
    assert output


def test_kiss_cov_columns_console():
    from rich._console_entry import Console
    from rich._columns_console import render_columns
    from rich.columns import Columns

    columns = Columns(["a", "b", "c"], padding=(0, 1))
    console = Console(file=io.StringIO(), width=40, color_system=None)
    tables = list(render_columns(columns, console, console.options))
    assert len(tables) == 1


def test_kiss_cov_tree_console():
    from rich._console_entry import Console
    from rich._tree_console import render_tree
    from rich.tree import Tree

    tree = Tree("root")
    tree.add("child")
    console = Console(file=io.StringIO(), width=40, color_system=None)
    segments = list(render_tree(tree, console, console.options))
    assert segments


def test_kiss_cov_console_collect():
    from rich._console_collect import append_collected_object
    from rich._console_entry import Console
    from rich._render_protocol import ConsoleRenderable

    console = Console(file=io.StringIO(), width=40, color_system=None)
    collected: list = []
    text_parts: list = []

    def append(item):
        collected.append(item)

    def append_text(item):
        text_parts.append(item)

    def check_text():
        if text_parts:
            collected.append("joined")
            text_parts.clear()

    append_collected_object(
        console,
        "hello",
        append=append,
        append_text=append_text,
        check_text=check_text,
        emoji=None,
        markup=None,
        highlight=None,
        highlighter=console.highlighter,
        text_class=type(console.render_str("x")),
        console_renderable_type=ConsoleRenderable,
        rich_cast=lambda obj: obj,
        is_expandable=lambda obj: False,
    )
    check_text()
    assert text_parts or collected
