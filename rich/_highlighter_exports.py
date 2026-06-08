"""Eager imports and registration for highlighter concrete types."""
from __future__ import annotations

from ._highlighter_registry import register_highlighters
from ._highlight_kernel import make_text
from ._iso8601_highlighter import ISO8601Highlighter
from ._json_highlight import register_json_highlight
from ._json_highlighter import JSONHighlighter
from ._null_highlighter import NullHighlighter
from ._regex_highlighter import RegexHighlighter, combine_regex
from ._repr_highlighter import ReprHighlighter
from ._highlighter_base import Highlighter

register_highlighters(
    base_class=Highlighter,
    repr_class=ReprHighlighter,
    repr_factory=ReprHighlighter,
    regex_class=RegexHighlighter,
)
register_json_highlight(JSONHighlighter().__call__, make_text)

__all__ = [
    "Highlighter",
    "NullHighlighter",
    "RegexHighlighter",
    "ReprHighlighter",
    "JSONHighlighter",
    "ISO8601Highlighter",
    "combine_regex",
]
