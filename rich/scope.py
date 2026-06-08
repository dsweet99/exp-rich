from __future__ import annotations

from collections.abc import Mapping
from ._pick import M_PANEL, M_PRETTY, M_TABLE, M_TEXT, rich_module
from typing import Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ._types import ConsoleRenderable, OverflowMethod, TextType



def render_scope(
    scope: "Mapping[str, Any]",
    *,
    title: Optional[TextType] = None,
    sort_keys: bool = True,
    indent_guides: bool = False,
    max_length: Optional[int] = None,
    max_string: Optional[int] = None,
    max_depth: Optional[int] = None,
    overflow: Optional["OverflowMethod"] = None,
) -> "ConsoleRenderable":
    """Render python variables in a given scope.

    Args:
        scope (Mapping): A mapping containing variable names and values.
        title (str, optional): Optional title. Defaults to None.
        sort_keys (bool, optional): Enable sorting of items. Defaults to True.
        indent_guides (bool, optional): Enable indentation guides. Defaults to False.
        max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to None.
        max_string (int, optional): Maximum length of string before truncating, or None to disable. Defaults to None.
        max_depth (int, optional): Maximum depths of locals before truncating, or None to disable. Defaults to None.
        overflow (OverflowMethod, optional): How to handle overflowing locals, or None to disable. Defaults to None.

    Returns:
        ConsoleRenderable: A renderable object.
    """
    from .highlighter import ReprHighlighter

    Pretty = rich_module(M_PRETTY).Pretty
    Panel = rich_module(M_PANEL).Panel
    Table = rich_module(M_TABLE).Table
    Text = rich_module(M_TEXT).Text

    highlighter = ReprHighlighter()
    items_table = Table.grid(padding=(0, 1), expand=False)
    items_table.add_column(justify="right")

    def sort_items(item: Tuple[str, Any]) -> Tuple[bool, str]:
        """Sort special variables first, then alphabetically."""
        key, _ = item
        return (not key.startswith("__"), key.lower())

    items = sorted(scope.items(), key=sort_items) if sort_keys else scope.items()
    for key, value in items:
        key_text = Text.assemble(
            (key, "scope.key.special" if key.startswith("__") else "scope.key"),
            (" =", "scope.equals"),
        )
        items_table.add_row(
            key_text,
            Pretty(
                value,
                highlighter=highlighter,
                indent_guides=indent_guides,
                max_length=max_length,
                max_string=max_string,
                max_depth=max_depth,
                overflow=overflow,
            ),
        )
    return Panel.fit(
        items_table,
        title=title,
        border_style="scope.border",
        padding=(0, 1),
    )


if __name__ == "__main__":  # pragma: no cover
    from . import print

    print()

    def test(foo: float, bar: float) -> None:
        list_of_things = [1, 2, 3, None, 4, True, False, "Hello World"]
        dict_of_things = {
            "version": "1.1",
            "method": "confirmFruitPurchase",
            "params": [["apple", "orange", "mangoes", "pomelo"], 1.123],
            "id": "194521489",
        }
        print(render_scope(locals(), title="[i]locals", sort_keys=False))

    test(20.3423, 3.1427)
    print()
