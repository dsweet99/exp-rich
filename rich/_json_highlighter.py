"""JSONHighlighter (one concrete type per file for kiss)."""
from __future__ import annotations

from typing import Any, ClassVar, Sequence

from ._highlight_kernel import span_class
from ._json_highlight import highlight_json_keys
from ._regex_highlighter import RegexHighlighter, combine_regex


class JSONHighlighter(RegexHighlighter):
    """Highlights JSON"""

    JSON_STR = r"(?<![\\\w])(?P<str>b?\".*?(?<!\\)\")"
    JSON_WHITESPACE = {" ", "\n", "\r", "\t"}

    base_style: ClassVar[str] = "json."
    highlights: ClassVar[Sequence[str]] = [
        combine_regex(
            r"(?P<brace>[\{\[\(\)\]\}])",
            r"\b(?P<bool_true>true)\b|\b(?P<bool_false>false)\b|\b(?P<null>null)\b",
            r"(?P<number>(?<!\w)\-?[0-9]+\.?[0-9]*(e[\-\+]?\d+?)?\b|0x[0-9a-fA-F]*)",
            JSON_STR,
        ),
    ]

    def highlight(self, text: Any) -> None:
        super().highlight(text)
        highlight_json_keys(text, self.JSON_STR, self.JSON_WHITESPACE, span_class())
