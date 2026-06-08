"""RegexHighlighter (one concrete type per file for kiss)."""
from __future__ import annotations

from typing import Any, ClassVar, Sequence

from ._highlighter_base import Highlighter


def combine_regex(*regexes: str) -> str:
    """Combine a number of regexes in to a single regex."""
    return "|".join(regexes)


class RegexHighlighter(Highlighter):
    """Applies highlighting from a list of regular expressions."""

    highlights: ClassVar[Sequence[str]] = []
    base_style: ClassVar[str] = ""

    def highlight(self, text: Any) -> None:
        """Highlight :class:`rich.text.Text` using regular expressions."""
        highlight_regex = text.highlight_regex
        for re_highlight in self.highlights:
            highlight_regex(re_highlight, style_prefix=self.base_style)
