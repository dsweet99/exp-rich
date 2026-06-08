"""Kiss static references for rich.markup code units."""

import rich.markup
from rich.markup import Tag, _parse, escape, render


def test_markup_module_and_units():
    assert rich.markup is not None
    tag = Tag("bold", None)
    assert tag.markup == "[bold]"
    assert str(tag) == "bold"
    assert escape("plain") == "plain"
    assert list(_parse("plain"))
    assert render("[green]x[/]").plain == "x"
    assert rich.markup.render("[green]y[/]").plain == "y"
