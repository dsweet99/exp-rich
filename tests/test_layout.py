import sys

import pytest


def test_no_layout():
    from rich.layout import Layout, NoSplitter

    layout = Layout()
    with pytest.raises(NoSplitter):
        layout.split(Layout(), Layout(), splitter="nope")


def test_add_split():
    from rich.layout import Layout

    layout = Layout()
    layout.split(Layout(), Layout())
    assert len(layout.children) == 2
    layout.add_split(Layout(name="foo"))
    assert len(layout.children) == 3
    assert layout.children[2].name == "foo"


def test_unsplit():
    from rich.layout import Layout

    layout = Layout()
    layout.split(Layout(), Layout())
    assert len(layout.children) == 2

    layout.unsplit()
    assert len(layout.children) == 0


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
def test_render():
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel

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
    from rich.console import Console
    from rich.layout import Layout

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
    from rich.console import Console
    from rich.layout import Layout

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
