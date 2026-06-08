"""ANSI decode_line helper (extracted for kiss)."""
from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Iterable

from ._ansi_sgr_map import SGR_STYLE_MAP
from ._ansi_token import AnsiToken as _AnsiToken

if TYPE_CHECKING:
    from .style import Style


def _apply_foreground(style: "Style", Style: type, Color: type, iter_codes: Iterable[int]) -> "Style":
    with suppress(StopIteration):
        color_type = next(iter_codes)
        if color_type == 5:
            return style + Style.from_color(Color.from_ansi(next(iter_codes)))
        if color_type == 2:
            return style + Style.from_color(
                Color.from_rgb(next(iter_codes), next(iter_codes), next(iter_codes))
            )
    return style


def _apply_background(style: "Style", Style: type, Color: type, iter_codes: Iterable[int]) -> "Style":
    with suppress(StopIteration):
        color_type = next(iter_codes)
        if color_type == 5:
            return style + Style.from_color(None, Color.from_ansi(next(iter_codes)))
        if color_type == 2:
            return style + Style.from_color(
                None,
                Color.from_rgb(next(iter_codes), next(iter_codes), next(iter_codes)),
            )
    return style


def _apply_sgr_code(
    code: int,
    style: "Style",
    Style: type,
    Color: type,
    iter_codes: Iterable[int],
) -> "Style":
    if code == 0:
        return Style.null()
    if code in SGR_STYLE_MAP:
        return style + Style.parse(SGR_STYLE_MAP[code])
    if code == 38:
        return _apply_foreground(style, Style, Color, iter_codes)
    if code == 48:
        return _apply_background(style, Style, Color, iter_codes)
    return style


def _apply_osc(style: "Style", osc: str) -> "Style":
    if not osc.startswith("8;"):
        return style
    _params, semicolon, link = osc[2:].partition(";")
    if semicolon:
        return style.update_link(link or None)
    return style


def _parse_sgr_codes(sgr: str) -> list[int]:
    return [
        min(255, int(_code) if _code else 0)
        for _code in sgr.split(";")
        if _code.isdigit() or _code == ""
    ]


def decode_line_tokens(
    line: str,
    style: "Style",
    Style: type,
    Color: type,
    Text: type,
    tokenize: Iterable[_AnsiToken],
) -> tuple[object, "Style"]:
    text = Text()
    append = text.append
    for plain_text, sgr, osc in tokenize:
        if plain_text:
            append(plain_text, style or None)
            continue
        if osc is not None:
            style = _apply_osc(style, osc)
            continue
        if sgr is None:
            continue
        iter_codes = iter(_parse_sgr_codes(sgr))
        for code in iter_codes:
            style = _apply_sgr_code(code, style, Style, Color, iter_codes)
    return text, style
