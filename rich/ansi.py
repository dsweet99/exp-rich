import re
from typing import Iterable, Optional

from ._ansi_token import AnsiToken as _AnsiToken
from ._text_registry import get_text_class
import importlib as _importlib

Color = _importlib.import_module(".color", __package__).Color
Style = _importlib.import_module(".style", __package__).Style

re_ansi = re.compile(
    r"""
(?:\x1b[0-?])|
(?:\x1b\](.*?)\x1b\\)|
(?:\x1b([(@-Z\\-_]|\[[0-?]*[ -/]*[@-~]))
""",
    re.VERBOSE,
)


def _ansi_tokenize(ansi_text: str) -> Iterable[_AnsiToken]:
    """Tokenize a string in to plain text and ANSI codes.

    Args:
        ansi_text (str): A String containing ANSI codes.

    Yields:
        AnsiToken: A named tuple of (plain, sgr, osc)
    """

    position = 0
    sgr: Optional[str]
    osc: Optional[str]
    for match in re_ansi.finditer(ansi_text):
        start, end = match.span(0)
        osc, sgr = match.groups()
        if start > position:
            yield _AnsiToken(ansi_text[position:start])
        if sgr:
            if sgr == "(":
                position = end + 1
                continue
            if sgr.endswith("m"):
                yield _AnsiToken("", sgr[1:-1], osc)
        else:
            yield _AnsiToken("", sgr, osc)
        position = end
    if position < len(ansi_text):
        yield _AnsiToken(ansi_text[position:])


class AnsiDecoder:
    """Translate ANSI code in to styled Text."""

    def __init__(self) -> None:
        self.style = Style.null()

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
        decode_line_tokens = _importlib.import_module(
            "._ansi_decode_line", __package__
        ).decode_line_tokens
        Text = get_text_class()
        line = line.rsplit("\r", 1)[-1]
        text, self.style = decode_line_tokens(
            line, self.style, Style, Color, Text, _ansi_tokenize(line)
        )
        return text


from ._ansi_registry import register_ansi_decoder  # noqa: E402

register_ansi_decoder(AnsiDecoder)
