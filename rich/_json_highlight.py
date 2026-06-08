"""Stdlib-only JSON highlight helpers (no rich imports)."""
from __future__ import annotations

import re
from typing import Any, Callable, FrozenSet, Optional, Type

_highlight_json: Optional[Callable[[str], Any]] = None
_make_text: Optional[Callable[[str], Any]] = None


def register_json_highlight(
    highlight_json: Callable[[str], Any],
    make_text: Callable[[str], Any],
) -> None:
    global _highlight_json, _make_text
    _highlight_json = highlight_json
    _make_text = make_text


def highlight_json(json: str, highlight: bool) -> Any:
    if _make_text is None or _highlight_json is None:
        raise RuntimeError(
            "JSON highlight not registered; import rich.text before rich.json"
        )
    if not highlight:
        return _make_text(json)
    return _highlight_json(json)


def highlight_json_keys(
    text: Any,
    json_str: str,
    whitespace: FrozenSet[str],
    span_class: Type[Any],
) -> None:
    """Mark JSON string keys in an already regex-highlighted text."""
    plain = text.plain
    append = text.spans.append
    for match in re.finditer(json_str, plain):
        start, end = match.span()
        cursor = end
        while cursor < len(plain):
            char = plain[cursor]
            cursor += 1
            if char == ":":
                append(span_class(start, end, "json.key"))
                break
            if char not in whitespace:
                break
