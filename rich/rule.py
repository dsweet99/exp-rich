from __future__ import annotations

from typing import Union, TYPE_CHECKING

from ._align_types import AlignMethod
from .cells import cell_len, set_cell_size
from ._jupyter_mixin import JupyterMixin
from ._lazy import Lazy
from ._pick import M_STYLE, M_TEXT, rich_module
from .measure import Measurement

if TYPE_CHECKING:
    from ._types import ConsoleOptions, RenderResult



def _Text():
    return rich_module(M_TEXT).Text


def _Style():
    return rich_module(M_STYLE).Style


Text = Lazy(_Text)
Style = Lazy(_Style)


def _rule_resolve_characters(characters: str, ascii_only: bool) -> str:
    if ascii_only and not characters.isascii():
        return "-"
    return characters


def _rule_build_aligned(
    align: AlignMethod,
    title_text: Text,
    characters: str,
    chars_len: int,
    width: int,
    style: Union[str, Style],
    end: str,
) -> Text:
    rule_text = Text(end=end)
    if align == "center":
        title_text.truncate(max(0, width - 4), overflow="ellipsis")
        side_width = (width - cell_len(title_text.plain)) // 2
        left = Text(characters * (side_width // chars_len + 1))
        left.truncate(side_width - 1)
        right_length = width - cell_len(left.plain) - cell_len(title_text.plain)
        right = Text(characters * (side_width // chars_len + 1))
        right.truncate(right_length)
        rule_text.append(left.plain + " ", style)
        rule_text.append(title_text)
        rule_text.append(" " + right.plain, style)
    elif align == "left":
        title_text.truncate(max(0, width - 2), overflow="ellipsis")
        rule_text.append(title_text)
        rule_text.append(" ")
        rule_text.append(characters * (width - rule_text.cell_len), style)
    else:
        title_text.truncate(max(0, width - 2), overflow="ellipsis")
        rule_text.append(characters * (width - title_text.cell_len - 1), style)
        rule_text.append(" ")
        rule_text.append(title_text)
    rule_text.plain = set_cell_size(rule_text.plain, width)
    return rule_text


class Rule(JupyterMixin):
    """A console renderable to draw a horizontal rule (line).

    Args:
        title (Union[str, Text], optional): Text to render in the rule. Defaults to "".
        characters (str, optional): Character(s) used to draw the line. Defaults to "─".
        style (StyleType, optional): Style of Rule. Defaults to "rule.line".
        end (str, optional): Character at end of Rule. defaults to "\\\\n"
        align (str, optional): How to align the title, one of "left", "center", or "right". Defaults to "center".
    """

    def __init__(
        self,
        title: Union[str, Text] = "",
        *,
        characters: str = "─",
        style: Union[str, Style] = "rule.line",
        end: str = "\n",
        align: AlignMethod = "center",
    ) -> None:
        if cell_len(characters) < 1:
            raise ValueError(
                "'characters' argument must have a cell width of at least 1"
            )
        if align not in ("left", "center", "right"):
            raise ValueError(
                f'invalid value for align, expected "left", "center", "right" (not {align!r})'
            )
        self.title = title
        self.characters = characters
        self.style = style
        self.end = end
        self.align = align

    def __repr__(self) -> str:
        return f"Rule({self.title!r}, {self.characters!r})"

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> RenderResult:
        width = options.max_width
        characters = _rule_resolve_characters(
            self.characters, options.ascii_only
        )
        chars_len = cell_len(characters)
        if not self.title:
            yield self._rule_line(chars_len, width)
            return

        _TextCls = _Text()
        title_text = (
            self.title
            if isinstance(self.title, _TextCls)
            else console.render_str(self.title, style="rule.text")
        )
        title_text.plain = title_text.plain.replace("\n", " ")
        title_text.expand_tabs()

        required_space = 4 if self.align == "center" else 2
        if max(0, width - required_space) == 0:
            yield self._rule_line(chars_len, width)
            return

        yield _rule_build_aligned(
            self.align, title_text, characters, chars_len, width, self.style, self.end
        )

    def _rule_line(self, chars_len: int, width: int) -> Text:
        rule_text = Text(self.characters * ((width // chars_len) + 1), self.style)
        rule_text.truncate(width)
        rule_text.plain = set_cell_size(rule_text.plain, width)
        return rule_text

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement(1, 1)


if __name__ == "__main__":  # pragma: no cover
    import importlib
    import sys

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    Console = importlib.import_module(_pkg + ".console").Console

    try:
        text = sys.argv[1]
    except IndexError:
        text = "Hello, World"
    console = Console()
    console.print(Rule(title=text))

    console = Console()
    console.print(Rule("foo"), width=4)
