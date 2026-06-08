"""Dedicated static references for rich.markup.render (avoids name collisions)."""

from __future__ import annotations

from rich.markup import render_markup as markup_render

markup_render("plain")
markup_render("[bold]x[/bold]")


def test_markup_render_alias_runs():
    assert markup_render("hello").plain == "hello"
