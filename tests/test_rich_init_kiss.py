"""Kiss static references for rich package entrypoints."""

import io

from rich import get_console, rich_print, rich_print_json
from rich.__main__ import ColorBox, make_test_card
from rich.console import Console


def test_get_console_direct_and_cached():
    console_a = get_console()
    console_b = get_console()
    assert console_a is console_b
    assert isinstance(console_a, Console)


def test_rich_init_print_and_print_json():
    import rich

    console = Console(file=io.StringIO())
    backup = rich.get_console().file
    try:
        rich.get_console().file = console.file
        rich_print("kiss")
        rich_print_json(data={"kiss": True})
    finally:
        rich.get_console().file = backup
    assert "kiss" in console.file.getvalue()


def test_rich_main_colorbox():
    console = Console(file=io.StringIO(), width=80)
    console.print(ColorBox())
    console.print(make_test_card())
    assert console.file.getvalue()
