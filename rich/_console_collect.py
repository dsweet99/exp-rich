"""Console._collect_renderables helpers (extracted for kiss)."""
from __future__ import annotations

from typing import Any, Callable


def append_collected_object(
    console: Any,
    renderable: Any,
    *,
    append: Callable[[Any], None],
    append_text: Callable[[Any], None],
    check_text: Callable[[], None],
    emoji: bool | None,
    markup: bool | None,
    highlight: bool | None,
    highlighter: Any,
    text_class: type,
    console_renderable_type: type,
    rich_cast: Callable[[Any], Any],
    is_expandable: Callable[[Any], bool],
) -> None:
    renderable = rich_cast(renderable)
    if isinstance(renderable, str):
        append_text(
            console.render_str(
                renderable,
                emoji=emoji,
                markup=markup,
                highlight=highlight,
                highlighter=highlighter,
            )
        )
    elif isinstance(renderable, text_class):
        append_text(renderable)
    elif isinstance(renderable, console_renderable_type):
        check_text()
        append(renderable)
    elif is_expandable(renderable):
        check_text()
        from rich.pretty import Pretty

        append(Pretty(renderable, highlighter=highlighter))
    else:
        append_text(highlighter(str(renderable)))
