import importlib as _importlib
import re
from typing import Callable, Iterable, List, Match, NamedTuple, Optional, Tuple, Union, Any

from ._emoji_replace import _emoji_replace
from ._no_emoji import EmojiVariant
from .style import Style

def _text_class():
    return _importlib.import_module(".text", __package__).Text


def _span_class():
    return _importlib.import_module(".text", __package__).Span


RE_TAGS = re.compile(
    r"""((\\*)\[([a-z#/@][^[]*?)])""",
    re.VERBOSE,
)

RE_HANDLER = re.compile(r"^([\w.]*?)(\(.*?\))?$")


def _escape_backslashes(match: Match[str]) -> str:
    """Called by re.sub replace matches."""
    backslashes, text = match.groups()
    return f"{backslashes}{backslashes}\\{text}"


class Tag(NamedTuple):
    """A tag in console markup."""

    name: str
    """The tag name. e.g. 'bold'."""
    parameters: Optional[str]
    """Any additional parameters after the name."""

    def __str__(self) -> str:
        return (
            self.name if self.parameters is None else f"{self.name} {self.parameters}"
        )

    @property
    def markup(self) -> str:
        """Get the string representation of this tag."""
        return (
            f"[{self.name}]"
            if self.parameters is None
            else f"[{self.name}={self.parameters}]"
        )


def _pop_style(style_stack: List[Tuple[int, Tag]], style_name: str) -> Tuple[int, Tag]:
    """Pop tag matching given style name."""
    pop = style_stack.pop
    for index, (_, tag) in enumerate(reversed(style_stack), 1):
        if tag.name == style_name:
            return pop(-index)
    raise KeyError(style_name)


_ReStringMatch = Match[str]  # regex match object
_ReSubCallable = Callable[[_ReStringMatch], str]  # Callable invoked by re.sub
_EscapeSubMethod = Callable[[_ReSubCallable, str], str]  # Sub method of a compiled re


def escape(
    markup: str,
    _escape: _EscapeSubMethod = re.compile(r"(\\*)(\[[a-z#/@][^[]*?])").sub,
) -> str:
    """Escapes text so that it won't be interpreted as markup.

    Args:
        markup (str): Content to be inserted in to markup.

    Returns:
        str: Markup with square brackets escaped.
    """

    markup = _escape(_escape_backslashes, markup)
    if markup.endswith("\\") and not markup.endswith("\\\\"):
        return markup + "\\"

    return markup


def _parse(markup: str) -> Iterable[Tuple[int, Optional[str], Optional[Tag]]]:
    """Parse markup in to an iterable of tuples of (position, text, tag).

    Args:
        markup (str): A string containing console markup

    """
    position = 0
    _divmod = divmod
    _Tag = Tag
    for match in RE_TAGS.finditer(markup):
        full_text, escapes, tag_text = match.groups()
        start, end = match.span()
        if start > position:
            yield start, markup[position:start], None
        if escapes:
            backslashes, escaped = _divmod(len(escapes), 2)
            if backslashes:
                # Literal backslashes
                yield start, "\\" * backslashes, None
                start += backslashes * 2
            if escaped:
                # Escape of tag
                yield start, full_text[len(escapes) :], None
                position = end
                continue
        text, equals, parameters = tag_text.partition("=")
        yield start, None, _Tag(text, parameters if equals else None)
        position = end
    if position < len(markup):
        yield position, markup[position:], None


def _render_without_tags(
    markup: str,
    style: Union[str, Style],
    emoji: bool,
    emoji_variant: Optional[EmojiVariant],
) -> Any:
    Text = _text_class()
    emoji_replace = _emoji_replace
    return Text(
        emoji_replace(markup, default_variant=emoji_variant) if emoji else markup,
        style=style,
    )


def _render_with_tags(
    markup: str,
    style: Union[str, Style],
    emoji: bool,
) -> Any:
    from ._markup_render_tags import render_with_tags

    return render_with_tags(
        markup,
        style,
        emoji,
        _text_class(),
        _span_class(),
        Tag,
        _emoji_replace,
        _parse,
        _pop_style,
        RE_HANDLER,
    )


def render_markup(
    markup: str,
    style: Union[str, Style] = "",
    emoji: bool = True,
    emoji_variant: Optional[EmojiVariant] = None,
) -> Any:
    """Render console markup in to a Text instance.

    Args:
        markup (str): A string containing console markup.
        style: (Union[str, Style]): The style to use.
        emoji (bool, optional): Also render emoji code. Defaults to True.
        emoji_variant (str, optional): Optional emoji variant, either "text" or "emoji". Defaults to None.


    Raises:
        MarkupError: If there is a syntax error in the markup.

    Returns:
        Text: A test instance.
    """
    return (
        _render_without_tags(markup, style, emoji, emoji_variant)
        if "[" not in markup
        else _render_with_tags(markup, style, emoji)
    )


render = render_markup


from ._markup_registry import register_render_markup  # noqa: E402

register_render_markup(render_markup)
