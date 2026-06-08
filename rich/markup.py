import re
from ast import literal_eval
from operator import attrgetter
from typing import Any, Callable, Iterable, List, Match, NamedTuple, Optional, Tuple, Union

from ._emoji_replace import _emoji_replace
from ._emoji_variant import EmojiVariant
from .errors import MarkupError
from .style import Style
from ._highlight_bridge import make_span, text_create

RE_TAGS = re.compile(
    r"""((\\*)\[([a-z#/@][^[]*?)])""",
    re.VERBOSE,
)

RE_HANDLER = re.compile(r"^([\w.]*?)(\(.*?\))?$")


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

    markup = _escape(
        lambda match: (
            f"{match.group(1)}{match.group(1)}\\{match.group(2)}"
        ),
        markup,
    )
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


def _render_unmarked(
    markup: str,
    style: Union[str, Style],
    emoji: bool,
    emoji_variant: Optional[EmojiVariant],
) -> Any:
    plain = (
        _emoji_replace(markup, default_variant=emoji_variant) if emoji else markup
    )
    return text_create(plain, style=style)


def _pop_style_from_stack(
    style_stack: List[Tuple[int, Tag]], style_name: str
) -> Tuple[int, Tag]:
    pop = style_stack.pop
    for index, (_, tag) in enumerate(reversed(style_stack), 1):
        if tag.name == style_name:
            return pop(-index)
    raise KeyError(style_name)


def _handler_meta_params(tag: Tag) -> tuple:
    if not tag.parameters:
        return ()
    handler_name = ""
    parameters = tag.parameters.strip()
    handler_match = RE_HANDLER.match(parameters)
    if handler_match is not None:
        handler_name, match_parameters = handler_match.groups()
        parameters = "()" if match_parameters is None else match_parameters
    try:
        meta_params = literal_eval(parameters)
    except SyntaxError as error:
        raise MarkupError(
            f"error parsing {parameters!r} in {tag.parameters!r}; {error.msg}"
        ) from None
    except Exception as error:
        raise MarkupError(f"error parsing {tag.parameters!r}; {error}") from None
    if not handler_name:
        return meta_params if isinstance(meta_params, tuple) else (meta_params,)
    payload = meta_params if isinstance(meta_params, tuple) else (meta_params,)
    return handler_name, payload


def _pop_closing_tag(
    tag: Tag,
    position: int,
    style_stack: List[Tuple[int, Tag]],
) -> Tuple[int, Tag]:
    style_name = tag.name[1:].strip()
    if style_name:
        style_name = Style.normalize(style_name)
        try:
            return _pop_style_from_stack(style_stack, style_name)
        except KeyError:
            raise MarkupError(
                f"closing tag '{tag.markup}' at position {position} doesn't match any open tag"
            ) from None
    try:
        return style_stack.pop()
    except IndexError:
        raise MarkupError(
            f"closing tag '[/]' at position {position} has nothing to close"
        ) from None


def _close_markup_tag(
    tag: Tag,
    position: int,
    style_stack: List[Tuple[int, Tag]],
    text: Any,
    spans: List[Any],
) -> None:
    start, open_tag = _pop_closing_tag(tag, position, style_stack)
    if open_tag.name.startswith("@"):
        meta_params = _handler_meta_params(open_tag)
        spans.append(
            make_span(start, len(text), Style(meta={open_tag.name: meta_params}))
        )
        return
    spans.append(make_span(start, len(text), str(open_tag)))


def _apply_markup_token(
    position: int,
    plain_text: Optional[str],
    tag: Optional[Tag],
    text: Any,
    style_stack: List[Tuple[int, Tag]],
    spans: List[Any],
    emoji: bool,
) -> None:
    if plain_text is not None:
        plain_text = plain_text.replace("\\[", "[")
        text.append(_emoji_replace(plain_text) if emoji else plain_text)
        return
    if tag is None:
        return
    if tag.name.startswith("/"):
        _close_markup_tag(tag, position, style_stack, text, spans)
        return
    style_stack.append((len(text), Tag(Style.normalize(tag.name), tag.parameters)))


def _finalize_markup_spans(text: Any, style_stack: List[Tuple[int, Tag]], spans: List[Any]) -> None:
    text_length = len(text)
    for start, tag in style_stack:
        span_style = str(tag)
        if span_style:
            spans.append(make_span(start, text_length, span_style))
    text.spans = sorted(spans[::-1], key=attrgetter("start"))


def render_console_markup(
    markup: str,
    style: Union[str, Style] = "",
    emoji: bool = True,
    emoji_variant: Optional[EmojiVariant] = None,
) -> Any:
    """Render console markup in to a Text instance."""
    if "[" not in markup:
        return _render_unmarked(markup, style, emoji, emoji_variant)

    text = text_create(style=style)
    style_stack: List[Tuple[int, Tag]] = []
    spans: List[Any] = []

    for position, plain_text, tag in _parse(markup):
        _apply_markup_token(position, plain_text, tag, text, style_stack, spans, emoji)

    _finalize_markup_spans(text, style_stack, spans)
    return text


render = render_console_markup

from ._highlight_bridge import configure_markup

configure_markup(render_console_markup, escape)
