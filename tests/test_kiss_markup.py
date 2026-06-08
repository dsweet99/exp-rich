"""Kiss symbol coverage for rich.markup."""

import pytest

from rich.errors import MarkupError
from rich.text import Text
from rich.markup import Tag, _parse, escape, render, render_console_markup


def test_kiss_markup_basics():
    tag = Tag("bold", "x")
    assert tag.markup == "[bold=x]"
    assert escape("[bold]") == r"\[bold]"
    assert list(_parse("[bold]x[/bold]"))
    assert render("plain", emoji=False).plain == "plain"
    assert render_console_markup("[green]x[/]").plain == "x"


def test_kiss_markup_errors():
    with pytest.raises(MarkupError):
        render("foo[/]")
    assert Text.from_markup("[bold]x[/bold]").plain == "x"
