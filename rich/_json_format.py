import re
import json as _stdlib_json
from typing import Any, Callable, Optional, Union

from ._highlight_bridge import make_span, text_create

_JSON_STR = r'(?<![\\\w])(?P<str>b?".*?(?<!\\)")'
_JSON_WHITESPACE = {" ", "\n", "\r", "\t"}
_JSON_HIGHLIGHTS = (
    r"(?P<brace>[\{\[\(\)\]\}])|"
    r"\b(?P<bool_true>true)\b|\b(?P<bool_false>false)\b|\b(?P<null>null)\b|"
    r"(?P<number>(?<!\w)\-?[0-9]+\.?[0-9]*(e[\-\+]?\d+?)?\b|0x[0-9a-fA-F]*)|"
    + _JSON_STR
)


def _mark_json_key(
    plain: str, start: int, end: int, append, whitespace: set[str]
) -> None:
    cursor = end
    while cursor < len(plain):
        char = plain[cursor]
        cursor += 1
        if char == ":":
            append(make_span(start, end, "json.key"))
            return
        if char not in whitespace:
            return


def highlight_json_text(text: Any) -> Any:
    text.highlight_regex(_JSON_HIGHLIGHTS, style_prefix="json.")
    plain = text.plain
    append = text.spans.append
    for match in re.finditer(_JSON_STR, plain):
        start, end = match.span()
        _mark_json_key(plain, start, end, append, _JSON_WHITESPACE)
    return text


def encode_json_text(
    data: Any,
    *,
    indent: Union[None, int, str] = 2,
    highlight: bool = True,
    skip_keys: bool = False,
    ensure_ascii: bool = False,
    check_circular: bool = True,
    allow_nan: bool = True,
    default: Optional[Callable[[Any], Any]] = None,
    sort_keys: bool = False,
) -> Any:
    json_string = _stdlib_json.dumps(
        data,
        indent=indent,
        skipkeys=skip_keys,
        ensure_ascii=ensure_ascii,
        check_circular=check_circular,
        allow_nan=allow_nan,
        default=default,
        sort_keys=sort_keys,
    )
    text = text_create(json_string)
    if highlight:
        highlight_json_text(text)
    text.no_wrap = True
    text.overflow = None
    return text
