# ruff: noqa: E402
from collections.abc import Mapping
from typing import Any, Optional, Tuple

from ._align_types import OverflowMethod
from ._highlighter_registry import repr_highlighter
from ._render_factory import table_grid
import importlib as _importlib

Panel = _importlib.import_module(".panel", __package__).Panel
Pretty = _importlib.import_module(".pretty", __package__).Pretty
from .text import Text, TextType
from ._render_protocol import ConsoleRenderable

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
    highlighter = repr_highlighter()
    items_table = table_grid(padding=(0, 1), expand=False)
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
