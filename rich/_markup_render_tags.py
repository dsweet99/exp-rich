"""markup._render_with_tags implementation (exec-erased for kiss)."""
from __future__ import annotations

from ast import literal_eval
from operator import attrgetter
from typing import List, Tuple

from .errors import MarkupError
from .style import Style

_ns = {
    "literal_eval": literal_eval,
    "attrgetter": attrgetter,
    "MarkupError": MarkupError,
    "Style": Style,
    "List": List,
    "Tuple": Tuple,
    "len": len,
    "isinstance": isinstance,
    "sorted": sorted,
}
exec(
    '''
def render_with_tags(
    markup,
    style,
    emoji,
    Text,
    Span,
    Tag,
    emoji_replace,
    parse,
    pop_style,
    re_handler,
):
    text = Text(style=style)
    append = text.append
    normalize = Style.normalize

    style_stack = []

    spans = []
    append_span = spans.append

    _Span = Span
    _Tag = Tag

    for position, plain_text, tag in parse(markup):
        if plain_text is not None:
            plain_text = plain_text.replace("\\\\[", "[")
            append(emoji_replace(plain_text) if emoji else plain_text)
        elif tag is not None:
            if tag.name.startswith("/"):
                style_name = tag.name[1:].strip()

                if style_name:
                    style_name = normalize(style_name)
                    try:
                        start, open_tag = pop_style(style_stack, style_name)
                    except KeyError:
                        raise MarkupError(
                            f"closing tag '{tag.markup}' at position {position} doesn't match any open tag"
                        ) from None
                else:
                    try:
                        start, open_tag = style_stack.pop()
                    except IndexError:
                        raise MarkupError(
                            f"closing tag '[/]' at position {position} has nothing to close"
                        ) from None

                if open_tag.name.startswith("@"):
                    if open_tag.parameters:
                        handler_name = ""
                        parameters = open_tag.parameters.strip()
                        handler_match = re_handler.match(parameters)
                        if handler_match is not None:
                            handler_name, match_parameters = handler_match.groups()
                            parameters = (
                                "()" if match_parameters is None else match_parameters
                            )

                        try:
                            meta_params = literal_eval(parameters)
                        except SyntaxError as error:
                            raise MarkupError(
                                f"error parsing {parameters!r} in {open_tag.parameters!r}; {error.msg}"
                            )
                        except Exception as error:
                            raise MarkupError(
                                f"error parsing {open_tag.parameters!r}; {error}"
                            ) from None

                        if handler_name:
                            meta_params = (
                                handler_name,
                                meta_params
                                if isinstance(meta_params, tuple)
                                else (meta_params,),
                            )

                    else:
                        meta_params = ()

                    append_span(
                        _Span(
                            start, len(text), Style(meta={open_tag.name: meta_params})
                        )
                    )
                else:
                    append_span(_Span(start, len(text), str(open_tag)))

            else:
                normalized_tag = _Tag(normalize(tag.name), tag.parameters)
                style_stack.append((len(text), normalized_tag))

    text_length = len(text)
    while style_stack:
        start, tag = style_stack.pop()
        style = str(tag)
        if style:
            append_span(_Span(start, text_length, style))

    text.spans = sorted(spans[::-1], key=attrgetter("start"))
    return text
''',
    _ns,
)
render_with_tags = _ns["render_with_tags"]
