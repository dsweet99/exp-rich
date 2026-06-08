from __future__ import annotations

import re
from contextlib import suppress
from typing import Callable, Iterable, Iterator, Optional, Tuple

from ._pick import M_COLOR, M_STYLE, M_TEXT, rich_module


def _Color() -> type:
    return rich_module(M_COLOR).Color


def _Style() -> type:
    return rich_module(M_STYLE).Style


def _Text() -> type:
    return rich_module(M_TEXT).Text

re_ansi = re.compile(
    r"""
(?:\x1b[0-?])|
(?:\x1b\](.*?)\x1b\\)|
(?:\x1b([(@-Z\\-_]|\[[0-?]*[ -/]*[@-~]))
""",
    re.VERBOSE,
)


_AnsiToken = Tuple[str, Optional[str], Optional[str]]


def _ansi_tokenize(ansi_text: str) -> Iterable[_AnsiToken]:
    """Tokenize a string in to plain text and ANSI codes.

    Args:
        ansi_text (str): A String containing ANSI codes.

    Yields:
        AnsiToken: A tuple of (plain, sgr, osc)
    """

    position = 0
    sgr: Optional[str]
    osc: Optional[str]
    for match in re_ansi.finditer(ansi_text):
        start, end = match.span(0)
        osc, sgr = match.groups()
        if start > position:
            yield (ansi_text[position:start], "", "")
        if sgr:
            if sgr == "(":
                position = end + 1
                continue
            if sgr.endswith("m"):
                yield ("", sgr[1:-1], osc)
        else:
            yield ("", sgr, osc)
        position = end
    if position < len(ansi_text):
        yield (ansi_text[position:], "", "")


SGR_STYLE_MAP = {
    1: "bold",
    2: "dim",
    3: "italic",
    4: "underline",
    5: "blink",
    6: "blink2",
    7: "reverse",
    8: "conceal",
    9: "strike",
    21: "underline2",
    22: "not dim not bold",
    23: "not italic",
    24: "not underline",
    25: "not blink",
    26: "not blink2",
    27: "not reverse",
    28: "not conceal",
    29: "not strike",
    30: "color(0)",
    31: "color(1)",
    32: "color(2)",
    33: "color(3)",
    34: "color(4)",
    35: "color(5)",
    36: "color(6)",
    37: "color(7)",
    39: "default",
    40: "on color(0)",
    41: "on color(1)",
    42: "on color(2)",
    43: "on color(3)",
    44: "on color(4)",
    45: "on color(5)",
    46: "on color(6)",
    47: "on color(7)",
    49: "on default",
    51: "frame",
    52: "encircle",
    53: "overline",
    54: "not frame not encircle",
    55: "not overline",
    90: "color(8)",
    91: "color(9)",
    92: "color(10)",
    93: "color(11)",
    94: "color(12)",
    95: "color(13)",
    96: "color(14)",
    97: "color(15)",
    100: "on color(8)",
    101: "on color(9)",
    102: "on color(10)",
    103: "on color(11)",
    104: "on color(12)",
    105: "on color(13)",
    106: "on color(14)",
    107: "on color(15)",
}


def _apply_osc_sequence(decoder: "AnsiDecoder", osc: str) -> None:
    if osc.startswith("8;"):
        _params, semicolon, link = osc[2:].partition(";")
        if semicolon:
            decoder.style = decoder.style.update_link(link or None)


def _apply_foreground_color(
    decoder: "AnsiDecoder",
    iter_codes: Iterable[int],
    *,
    from_ansi: Callable[..., object],
    from_rgb: Callable[..., object],
) -> None:
    Style = _Style()
    with suppress(StopIteration):
        color_type = next(iter_codes)
        if color_type == 5:
            decoder.style += Style.from_color(from_ansi(next(iter_codes)))
        elif color_type == 2:
            decoder.style += Style.from_color(
                from_rgb(
                    next(iter_codes),
                    next(iter_codes),
                    next(iter_codes),
                )
            )


def _apply_background_color(
    decoder: "AnsiDecoder",
    iter_codes: Iterable[int],
    *,
    from_ansi: Callable[..., object],
    from_rgb: Callable[..., object],
) -> None:
    Style = _Style()
    with suppress(StopIteration):
        color_type = next(iter_codes)
        if color_type == 5:
            decoder.style += Style.from_color(None, from_ansi(next(iter_codes)))
        elif color_type == 2:
            decoder.style += Style.from_color(
                None,
                from_rgb(
                    next(iter_codes),
                    next(iter_codes),
                    next(iter_codes),
                ),
            )


def _apply_sgr_code(
    decoder: "AnsiDecoder",
    code: int,
    iter_codes: Iterable[int],
    *,
    from_ansi: Callable[..., object],
    from_rgb: Callable[..., object],
) -> None:
    Style = _Style()
    if code == 0:
        decoder.style = Style.null()
    elif code in SGR_STYLE_MAP:
        decoder.style += Style.parse(SGR_STYLE_MAP[code])
    elif code == 38:
        _apply_foreground_color(
            decoder, iter_codes, from_ansi=from_ansi, from_rgb=from_rgb
        )
    elif code == 48:
        _apply_background_color(
            decoder, iter_codes, from_ansi=from_ansi, from_rgb=from_rgb
        )


def _decode_ansi_token(
    decoder: "AnsiDecoder",
    text: object,
    plain_text: str,
    sgr: Optional[str],
    osc: Optional[str],
) -> None:
    Color = _Color()
    append = text.append
    if plain_text:
        append(plain_text, decoder.style or None)
    elif osc is not None:
        _apply_osc_sequence(decoder, osc)
    elif sgr is not None:
        from_ansi = Color.from_ansi
        from_rgb = Color.from_rgb
        codes = [
            min(255, int(_code) if _code else 0)
            for _code in sgr.split(";")
            if _code.isdigit() or _code == ""
        ]
        iter_codes: Iterator[int] = iter(codes)
        for code in iter_codes:
            _apply_sgr_code(
                decoder, code, iter_codes, from_ansi=from_ansi, from_rgb=from_rgb
            )


class AnsiDecoder:
    """Translate ANSI code in to styled Text."""

    def __init__(self) -> None:
        self.style = _Style().null()

    def decode(self, terminal_text: str) -> Iterable[object]:
        """Decode ANSI codes in an iterable of lines.

        Args:
            terminal_text: Output potentially containing ANSI escape sequences.

        Yields:
            Text: Marked up Text.
        """
        for line in re.split(r"(?<=\n)", terminal_text):
            yield self.decode_line(line.rstrip("\n"))

    def decode_line(self, line: str) -> object:
        """Decode a line containing ansi codes.

        Args:
            line (str): A line of terminal output.

        Returns:
            Text: A Text instance marked up according to ansi codes.
        """
        Text = _Text()
        text = Text()
        line = line.rsplit("\r", 1)[-1]
        for plain_text, sgr, osc in _ansi_tokenize(line):
            _decode_ansi_token(self, text, plain_text, sgr, osc)

        return text


if __name__ == "__main__":  # pragma: no cover
    import io
    import os
    import pty
    import sys

    if sys.platform == "win32":
        raise SystemExit(0)

    decoder = AnsiDecoder()

    stdout = io.BytesIO()

    def read(fd: int) -> bytes:
        data = os.read(fd, 1024)
        stdout.write(data)
        return data

    pty.spawn(sys.argv[1:], read)

    from .console import Console

    console = Console(record=True)

    stdout_result = stdout.getvalue().decode("utf-8")
    print(stdout_result)

    for line in decoder.decode(stdout_result):
        console.print(line)

    console.save_html("stdout.html")
