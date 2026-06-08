"""Syntax.highlight helpers (extracted for kiss)."""
from __future__ import annotations

from typing import Any, Iterable, Optional, Tuple

from .style import Style
from .text import Text


def append_highlighted_code(
    syntax: Any,
    text: Text,
    code: str,
    line_range: Optional[Tuple[Optional[int], Optional[int]]],
) -> None:
    """Append lexer tokens to *text*."""
    _get_theme_style = syntax._theme.get_style_for_token
    lexer = syntax.lexer or syntax.default_lexer
    if lexer is None:
        text.append(code)
        return

    if line_range:
        line_start, line_end = line_range
        text.append_tokens(
            _line_range_token_spans(
                lexer, code, line_start, line_end, _get_theme_style
            )
        )
    else:
        text.append_tokens(
            (token, _get_theme_style(token_type))
            for token_type, token in lexer.get_tokens(code)
        )
    if syntax.background_color is not None:
        text.stylize(f"on {syntax.background_color}")


def _line_range_token_spans(
    lexer: Any,
    code: str,
    line_start: Optional[int],
    line_end: Optional[int],
    get_theme_style: Any,
) -> Iterable[Tuple[str, Optional[Style]]]:
    tokens = iter(_line_tokenize(lexer, code))
    line_no = 0
    _line_start = line_start - 1 if line_start else 0

    while line_no < _line_start:
        try:
            _token_type, token = next(tokens)
        except StopIteration:
            break
        yield (token, None)
        if token.endswith("\n"):
            line_no += 1

    for token_type, token in tokens:
        yield (token, get_theme_style(token_type))
        if token.endswith("\n"):
            line_no += 1
            if line_end and line_no >= line_end:
                break


def _line_tokenize(lexer: Any, code: str) -> Iterable[Tuple[Any, str]]:
    for token_type, token in lexer.get_tokens(code):
        while token:
            line_token, new_line, token = token.partition("\n")
            yield token_type, line_token + new_line
