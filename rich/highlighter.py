import re
from abc import ABC, abstractmethod
from typing import ClassVar, NamedTuple, Sequence, Union

from ._highlight_bridge import copy_text, is_text, text_from_str

def _combine_regex(*regexes: str) -> str:
    """Combine a number of regexes in to a single regex.

    Returns:
        str: New regex with all regexes ORed together.
    """
    return '|'.join(regexes)

class Highlighter(ABC):
    """Abstract base class for highlighters."""

    def __call__(self, text: Union[str, 'Text']) -> 'Text':
        """Highlight a str or Text instance.

        Args:
            text (Union[str, ~Text]): Text to highlight.

        Raises:
            TypeError: If not called with text or str.

        Returns:
            Text: A test instance with highlighting applied.
        """
        if isinstance(text, str):
            highlight_text = text_from_str(text)
        elif is_text(text):
            highlight_text = copy_text(text)
        else:
            raise TypeError(f'str or Text instance required, not {text!r}')
        self.highlight(highlight_text)
        return highlight_text

    @abstractmethod
    def highlight(self, text: 'Text') -> None:
        """Apply highlighting in place to text.

        Args:
            text (~Text): A text object highlight.
        """

class NullHighlighter(Highlighter):
    """A highlighter object that doesn't highlight.

    May be used to disable highlighting entirely.

    """

    def highlight(self, text: 'Text') -> None:
        """Nothing to do"""

class RegexHighlighter(Highlighter):
    """Applies highlighting from a list of regular expressions."""
    highlights: ClassVar[Sequence[str]] = []
    base_style: ClassVar[str] = ''

    def highlight(self, text: 'Text') -> None:
        """Highlight :class:`rich.text.Text` using regular expressions.

        Args:
            text (~Text): Text to highlighted.

        """
        highlight_regex = text.highlight_regex
        for re_highlight in self.highlights:
            highlight_regex(re_highlight, style_prefix=self.base_style)

class ReprHighlighter(RegexHighlighter):
    """Highlights the text typically produced from ``__repr__`` methods."""
    base_style = 'repr.'
    highlights: ClassVar[Sequence[str]] = ['(?P<tag_start><)(?P<tag_name>[-\\w.:|]*)(?P<tag_contents>[\\w\\W]*)(?P<tag_end>>)', '(?P<attrib_name>[\\w_]{1,50})=(?P<attrib_value>"?[\\w_]+"?)?', '(?P<brace>[][{}()])', _combine_regex('(?P<ipv4>[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})', '(?P<ipv6>([A-Fa-f0-9]{1,4}::?){1,7}[A-Fa-f0-9]{1,4})', '(?P<eui64>(?:[0-9A-Fa-f]{1,2}-){7}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{1,2}:){7}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{4}\\.){3}[0-9A-Fa-f]{4})', '(?P<eui48>(?:[0-9A-Fa-f]{1,2}-){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{1,2}:){5}[0-9A-Fa-f]{1,2}|(?:[0-9A-Fa-f]{4}\\.){2}[0-9A-Fa-f]{4})', '(?P<uuid>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})', '(?P<call>[\\w.]*?)\\(', '\\b(?P<bool_true>True)\\b|\\b(?P<bool_false>False)\\b|\\b(?P<none>None)\\b', '(?P<ellipsis>\\.\\.\\.)', '(?P<number_complex>(?<!\\w)(?:\\-?[0-9]+\\.?[0-9]*(?:e[-+]?\\d+?)?)(?:[-+](?:[0-9]+\\.?[0-9]*(?:e[-+]?\\d+)?))?j)', '(?P<number>(?<!\\w)\\-?[0-9]+\\.?[0-9]*(e[-+]?\\d+?)?\\b|0x[0-9a-fA-F]*)', '(?P<path>\\B(/[-\\w._+]+)*\\/)(?P<filename>[-\\w._+]*)?', '(?<![\\\\\\w])(?P<str>b?\'\'\'.*?(?<!\\\\)\'\'\'|b?\'.*?(?<!\\\\)\'|b?\\"\\"\\".*?(?<!\\\\)\\"\\"\\"|b?\\".*?(?<!\\\\)\\")', '(?P<url>(file|https|http|ws|wss)://[-0-9a-zA-Z$_+!`(),.?/;:&=%#~@]*)')]

class _HighlightSpan(NamedTuple):
    start: int
    end: int
    style: str


def _mark_json_key(plain: str, start: int, end: int, append, whitespace: set[str]) -> None:
    cursor = end
    while cursor < len(plain):
        char = plain[cursor]
        cursor += 1
        if char == ':':
            append(_HighlightSpan(start, end, 'json.key'))
            return
        if char not in whitespace:
            return

class JSONHighlighter(RegexHighlighter):
    """Highlights JSON"""
    JSON_STR = '(?<![\\\\\\w])(?P<str>b?\\".*?(?<!\\\\)\\")'
    JSON_WHITESPACE = {' ', '\n', '\r', '\t'}
    base_style: ClassVar[str] = 'json.'
    highlights: ClassVar[Sequence[str]] = [_combine_regex('(?P<brace>[\\{\\[\\(\\)\\]\\}])', '\\b(?P<bool_true>true)\\b|\\b(?P<bool_false>false)\\b|\\b(?P<null>null)\\b', '(?P<number>(?<!\\w)\\-?[0-9]+\\.?[0-9]*(e[\\-\\+]?\\d+?)?\\b|0x[0-9a-fA-F]*)', JSON_STR)]

    def highlight(self, text: 'Text') -> None:
        super().highlight(text)
        plain = text.plain
        append = text.spans.append
        whitespace = self.JSON_WHITESPACE
        for match in re.finditer(self.JSON_STR, plain):
            start, end = match.span()
            _mark_json_key(plain, start, end, append, whitespace)

class ISO8601Highlighter(RegexHighlighter):
    """Highlights the ISO8601 date time strings.
    Regex reference: https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s07.html
    """
    base_style: ClassVar[str] = 'iso8601.'
    highlights: ClassVar[Sequence[str]] = ['^(?P<year>[0-9]{4})-(?P<month>1[0-2]|0[1-9])$', '^(?P<date>(?P<year>[0-9]{4})(?P<month>1[0-2]|0[1-9])(?P<day>3[01]|0[1-9]|[12][0-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?(?P<day>36[0-6]|3[0-5][0-9]|[12][0-9]{2}|0[1-9][0-9]|00[1-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9]))$', '^(?P<date>(?P<year>[0-9]{4})-?W(?P<week>5[0-3]|[1-4][0-9]|0[1-9])-?(?P<day>[1-7]))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9]):?(?P<minute>[0-5][0-9]))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))$', '^(?P<timezone>(Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?))$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9])(?P<minute>[0-5][0-9])(?P<second>[0-5][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9])(?::?(?:[0-5][0-9]))?)$', '^(?P<date>(?P<year>[0-9]{4})(?P<hyphen>-)?(?P<month>1[0-2]|0[1-9])(?(hyphen)-)(?P<day>3[01]|0[1-9]|[12][0-9])) (?P<time>(?P<hour>2[0-3]|[01][0-9])(?(hyphen):)(?P<minute>[0-5][0-9])(?(hyphen):)(?P<second>[0-5][0-9]))$', '^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$', '^(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<frac>\\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$', '^(?P<date>(?P<year>-?(?:[1-9][0-9]*)?[0-9]{4})-(?P<month>1[0-2]|0[1-9])-(?P<day>3[01]|0[1-9]|[12][0-9]))T(?P<time>(?P<hour>2[0-3]|[01][0-9]):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])(?P<ms>\\.[0-9]+)?)(?P<timezone>Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$']


class PathHighlighter(RegexHighlighter):
    """Highlight the last path component in file paths."""

    highlights = [r"(?P<dim>.*/)(?P<bold>.+)"]
