"""Explicit kiss coverage for rich.markup.render_console_markup."""

from rich.markup import render, render_console_markup


def test_markup_render_plain():
    assert render("hello").plain == "hello"
    assert render_console_markup("hello").plain == "hello"


def test_markup_render_styled():
    assert render("[bold]x[/bold]").plain == "x"
    assert render_console_markup("[bold]y[/bold]").plain == "y"
