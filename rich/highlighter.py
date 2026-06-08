from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Pattern, Union

from ._pick import M_TEXT, rich_module


def _is_text_instance(obj: Any) -> bool:
    return hasattr(obj, "plain") and hasattr(obj, "copy") and hasattr(obj, "highlight_regex")


def _text_from_string(value: str) -> Any:
    return _HighlightableText(value)


def _highlightable_to_text(highlight_text: "_HighlightableText") -> Any:
    result = rich_module(M_TEXT).Text(highlight_text.plain)
    for span in highlight_text.spans:
        result.stylize(span.style, span.start, span.end)
    return result


def _highlightable_text_init(self, value: str) -> None:
    self.plain = value
    self.spans: list = []


def _highlightable_text_copy(self) -> "_HighlightableText":
    copy = _HighlightableText(self.plain)
    copy.spans = self.spans[:]
    return copy


def _highlightable_text_stylize(
    self, style: str, start: int = 0, end: int | None = None
) -> None:
    if end is None:
        end = len(self.plain)
    self.spans.append(_HighlightSpan(start, end, style))


def _highlightable_text_highlight_regex(
    self,
    re_highlight: Union[str, Pattern[str]],
    style: Any = None,
    *,
    style_prefix: str = "",
) -> int:
    count = 0
    if isinstance(re_highlight, str):
        re_highlight = re.compile(re_highlight)
    for match in re_highlight.finditer(self.plain):
        if style:
            start, end = match.span()
            match_style = style(self.plain[start:end]) if callable(style) else style
            if match_style is not None and end > start:
                self.spans.append(_HighlightSpan(start, end, match_style))
        count += 1
        for name in match.groupdict().keys():
            start, end = match.span(name)
            if start != -1 and end > start:
                self.spans.append(_HighlightSpan(start, end, f"{style_prefix}{name}"))
    return count


_HighlightableText = type(
    "_HighlightableText",
    (),
    {
        "__doc__": "Minimal Text-compatible object for highlighting without importing rich.text.",
        "__slots__": ("plain", "spans"),
        "__init__": _highlightable_text_init,
        "copy": _highlightable_text_copy,
        "stylize": _highlightable_text_stylize,
        "highlight_regex": _highlightable_text_highlight_regex,
    },
)


def _highlight_span_init(self, start: int, end: int, style: str) -> None:
    self.start = start
    self.end = end
    self.style = style


def _highlight_span_eq(self, other: object) -> bool:
    return (
        isinstance(other, _HighlightSpan)
        and self.start == other.start
        and self.end == other.end
        and self.style == other.style
    )


_HighlightSpan = type(
    "Span",
    (),
    {
        "__slots__": ("start", "end", "style"),
        "__init__": _highlight_span_init,
        "__eq__": _highlight_span_eq,
    },
)


def _combine_regex(*regexes: str) -> str:
    """Combine a number of regexes in to a single regex.

    Returns:
        str: New regex with all regexes ORed together.
    """
    return "|".join(regexes)


class Highlighter(ABC):
    """Abstract base class for highlighters."""

    def __call__(self, text: Union[str, Any]) -> Any:
        """Highlight a str or Text instance.

        Args:
            text (Union[str, ~Text]): Text to highlight.

        Raises:
            TypeError: If not called with text or str.

        Returns:
            Text: A test instance with highlighting applied.
        """
        if isinstance(text, str):
            highlight_text = _text_from_string(text)
            self.highlight(highlight_text)
            return _highlightable_to_text(highlight_text)
        if _is_text_instance(text):
            highlight_text = text.copy()
            self.highlight(highlight_text)
            return highlight_text
        raise TypeError(f"str or Text instance required, not {text!r}")

    @abstractmethod
    def highlight(self, text: Any) -> None:
        """Apply highlighting in place to text.

        Args:
            text (~Text): A text object highlight.
        """


def _null_highlighter_highlight(self, text: Any) -> None:
    """Nothing to do"""


NullHighlighter = type(
    "NullHighlighter",
    (Highlighter,),
    {
        "__doc__": "A highlighter object that doesn't highlight.",
        "highlight": _null_highlighter_highlight,
    },
)


def _regex_highlighter_highlight(self, text: Any) -> None:
    highlight_regex = text.highlight_regex
    for re_highlight in self.highlights:
        highlight_regex(re_highlight, style_prefix=self.base_style)


RegexHighlighter = type(
    "RegexHighlighter",
    (Highlighter,),
    {
        "__doc__": "Applies highlighting from a list of regular expressions.",
        "highlights": [],
        "base_style": "",
        "highlight": _regex_highlighter_highlight,
    },
)


ReprHighlighter = type(
    "ReprHighlighter",
    (RegexHighlighter,),
    {
        "__doc__": "Highlights the text typically produced from ``__repr__`` methods.",
        "base_style": "repr.",
        "highlights": [
            r"(?P<tag_start><)(?P<tag_name>[-\w.:|]*)(?P<tag_contents>[\w\W]*)(?P<tag_end>>)",
            r'(?P<attrib_name>[\w_]{1,50})=(?P<attrib_value>"?[\w_]+"?)?',
            r"(?P<brace>[][{}()])",
            _combine_regex(
                r"(?P<ipv4>[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",
                r"(?P<ipv6>([A-Fa-f0-9]{1,4}::?){1,7}[A-Fa-f0-9]{1,4})",
                r"(?P<eui64>(?:[0-9A-Fa-f]{1,2}-){7}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{1,2}:){7}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{4}\.){3}[0-9A-Fa-f]{4})",
                r"(?P<eui48>(?:[0-9A-Fa-f]{1,2}-){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{1,2}:){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4})",
                r"(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})",
                r"(?P<call>[\w.]*?)\(",
                r"\b(?P<bool_true>True)\b|\b(?P<bool_false>False)\b|\b(?P<none>None)\b",
                r"(?P<ellipsis>\.\.\.)",
                r"(?P<number_complex>(?<!\w)(?:\-?[0-9]+\.?[0-9]*(?:e[-+]?\d+?)?)(?:[-+](?:[0-9]+\.?[0-9]*(?:e[-+]?\d+)?))?j)",
                r"(?P<number>(?<!\w)\-?[0-9]+\.?[0-9]*(e[-+]?\d+?)?\b|0x[0-9a-fA-F]*)",
                r"(?P<path>\B(/[-\w._+]+)*\/)(?P<filename>[-\w._+]*)?",
                r"(?<![\\\w])(?P<str>b?'''.*?(?<!\\)'''|b?'.*?(?<!\\)'|b?\"\"\".*?(?<!\\)\"\"\"|b?\".*?(?<!\\)\")",
                r"(?P<url>(file|https|http|ws|wss)://[-0-9a-zA-Z$_+!`(),.?/;:&=%#~@]*)",
            ),
        ],
    },
)


JSON_STR = r'(?<![\\\w])(?P<str>b?\".*?(?<!\\)\")'
JSON_WHITESPACE = {" ", "\n", "\r", "\t"}


def _json_scan_key_suffix(
    text: Any, plain: str, start: int, end: int
) -> None:
    cursor = end
    whitespace = JSON_WHITESPACE
    while cursor < len(plain):
        char = plain[cursor]
        cursor += 1
        if char == ":":
            text.stylize("json.key", start, end)
            return
        if char in whitespace:
            continue
        return


def _json_highlighter_highlight(self, text: Any) -> None:
    RegexHighlighter.highlight(self, text)
    plain = text.plain
    for match in re.finditer(JSON_STR, plain):
        start, end = match.span()
        _json_scan_key_suffix(text, plain, start, end)


JSONHighlighter = type(
    "JSONHighlighter",
    (RegexHighlighter,),
    {
        "__doc__": "Highlights JSON",
        "base_style": "json.",
        "highlights": [
            _combine_regex(
                r"(?P<brace>[\{\[\(\)\]\}])",
                r"\b(?P<bool_true>true)\b|\b(?P<bool_false>false)\b|\b(?P<null>null)\b",
                r"(?P<number>(?<!\w)\-?[0-9]+\.?[0-9]*(e[\-\+]?\d+?)?\b|0x[0-9a-fA-F]*)",
                JSON_STR,
            ),
        ],
        "highlight": _json_highlighter_highlight,
    },
)


ISO8601Highlighter = type(
    "ISO8601Highlighter",
    (RegexHighlighter,),
    {
        "__doc__": "Highlights the ISO8601 date time strings.",
        "base_style": "iso8601.",
        "highlights": [
            r"^(?P<year>[0-9]{4})-(?P<month>1[0-2]|0[1-9])$",
            r"^(?P<date>(?P<year>[0-9]{4})(?P<month>1[0-2]|0[1-9])(?P<day>3[01]|0[1-9]|[12][0-9]))$",
            r"^(?P<date>(?P<year>[0-9]{4})-?(?P<day>36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9]))$",
            r"^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9]))$",
            r"^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9])-?(?P<day>[1-7]))$",
            r"^(?P<time>(?P<hour>2[0-3]|[01][0-9]):?(?P<minute>[0-5][0-9]))$",
            r"^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))$",
            r"^(?P<timezone>(Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?))$",
            r"^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?)$",
            r"^(?P<date>(?P<year>[0-9]{4})(?P<hyphen>-)?(?P<month>1[0-2]|0[1-9])(?(hyphen)-)(?P<day>3[01]|0[1-9]|[12][0-9])) (?P<time>(?P<hour>2[0-3]|[01][0-9])(?(hyphen):)(?P<minute>[0-5][0-9])(?(hyphen):)(?P<second>[0-5][0-9]))$",
            r"^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
            r"^(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<frac>\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
            r"^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))T(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<ms>\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$",
        ],
    },
)
