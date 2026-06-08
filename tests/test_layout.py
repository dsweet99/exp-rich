import sys
import importlib as _importlib

import pytest

Console = _importlib.import_module("rich._console_entry").Console
Layout = _importlib.import_module("rich.layout").Layout
NoSplitter = _importlib.import_module("rich.layout").NoSplitter
Panel = _importlib.import_module("rich.panel").Panel


def test_no_layout():
    layout = Layout()
    with pytest.raises(NoSplitter):
        layout.split(Layout(), Layout(), splitter="nope")


def test_add_split():
    layout = Layout()
    layout.split(Layout(), Layout())
    assert len(layout.children) == 2
    layout.add_split(Layout(name="foo"))
    assert len(layout.children) == 3
    assert layout.children[2].name == "foo"


def test_unsplit():
    layout = Layout()
    layout.split(Layout(), Layout())
    assert len(layout.children) == 2

    layout.unsplit()
    assert len(layout.children) == 0


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_render():
    layout = Layout(name="root")
    repr(layout)

    layout.split_column(Layout(name="top"), Layout(name="bottom"))
    top = layout["top"]
    top.update(Panel("foo"))

    print(type(top._renderable))
    assert isinstance(top.renderable, Panel)
    layout["bottom"].split_row(Layout(name="left"), Layout(name="right"))

    assert layout["root"].name == "root"
    assert layout["left"].name == "left"

    assert isinstance(layout.map, dict)

    with pytest.raises(KeyError):
        top["asdasd"]

    layout["left"].update("foobar")
    print(layout["left"].children)

    console = Console(width=60, color_system=None)

    with console.capture() as capture:
        console.print(layout, height=10)

    result = capture.get()
    print(repr(result))
    expected = "╭──────────────────────────────────────────────────────────╮\n│ foo                                                      │\n│                                                          │\n│                                                          │\n╰──────────────────────────────────────────────────────────╯\nfoobar                        ╭───── 'right' (30 x 5) ─────╮\n                              │                            │\n                              │    Layout(name='right')    │\n                              │                            │\n                              ╰────────────────────────────╯\n"

    assert result == expected


def test_tree():
    layout = Layout(name="root")
    layout.split(Layout("foo", size=2), Layout("bar", name="bar"))
    layout["bar"].split_row(Layout(), Layout())

    console = Console(width=60, color_system=None)

    with console.capture() as capture:
        console.print(layout.tree, height=10)
    result = capture.get()
    print(repr(result))
    expected = "⬍ Layout(name='root')\n├── ⬍ Layout(size=2)\n└── ⬌ Layout(name='bar')\n    ├── ⬍ Layout()\n    └── ⬍ Layout()\n"
    print(result, "\n", expected)
    assert result == expected


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_refresh_screen():
    import rich.screen  # noqa: F401 — registers Screen for console.screen()

    layout = Layout()
    layout.split_row(Layout(name="foo"), Layout(name="bar"))
    console = Console(force_terminal=True, width=20, height=5, _environ={})
    with console.capture():
        console.print(layout)
    with console.screen():
        with console.capture() as capture:
            layout.refresh_screen(console, "foo")
    result = capture.get()
    print()
    print(repr(result))
    expected = "\x1b[1;1H\x1b[34m╭─\x1b[0m\x1b[34m \x1b[0m\x1b[32m'foo'\x1b[0m\x1b[34m─╮\x1b[0m\x1b[2;1H\x1b[34m│\x1b[0m \x1b[1;35mLayout\x1b[0m \x1b[34m│\x1b[0m\x1b[3;1H\x1b[34m│\x1b[0m \x1b[1m(\x1b[0m      \x1b[34m│\x1b[0m\x1b[4;1H\x1b[34m│\x1b[0m     \x1b[33mna\x1b[0m \x1b[34m│\x1b[0m\x1b[5;1H\x1b[34m╰────────╯\x1b[0m"
    assert result == expected


def test_split_row_tiles_width():
    layout = Layout()
    layout.split_row(Layout(ratio=1), Layout(ratio=2))
    region_map = layout._make_region_map(30, 10)
    leaves = [region_map[child] for child in layout.children]
    assert sum(r.width for r in leaves) == 30
    assert all(r.height == 10 for r in leaves)


def test_split_column_tiles_height():
    layout = Layout()
    layout.split_column(Layout(ratio=1), Layout(ratio=1))
    region_map = layout._make_region_map(20, 8)
    leaves = [region_map[child] for child in layout.children]
    assert sum(r.height for r in leaves) == 8
    assert all(r.width == 20 for r in leaves)


def test_nested_region_map_partitions_without_gaps():
    from rich.region import Region

    layout = Layout()
    layout.split_column(Layout(ratio=1, name="top"), Layout(ratio=1, name="bottom"))
    layout["top"].split_row(Layout(ratio=1), Layout(ratio=2))
    region_map = layout._make_region_map(60, 12)
    assert region_map[layout] == Region(0, 0, 60, 12)
    for child in layout._children:
        if not child.children:
            continue
        child_regions = [region_map[c] for c in child.children]
        parent_region = region_map[child]
        if child.splitter.name == "row":
            assert sum(r.width for r in child_regions) == parent_region.width
        else:
            assert sum(r.height for r in child_regions) == parent_region.height


def test_placeholder_renderable_when_no_content():
    import io

    layout = Layout(name="pane")
    console = Console(file=io.StringIO(), width=40, color_system=None)
    with console.capture() as capture:
        console.print(layout.renderable, height=4)
    output = capture.get()
    assert "pane" in output
    assert "Layout" in output
