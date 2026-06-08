from __future__ import annotations

from typing import Union

from .align import AlignMethod
from .cells import cell_len, set_cell_size
from .jupyter import JupyterMixin
from .measure import Measurement
from .style import Style
from .text import Text
from ._render_protocol import Console, ConsoleOptions, RenderResult


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

    def _title_text(self, console: Console) -> Text:
        if isinstance(self.title, Text):
            title_text = self.title
        else:
            title_text = console.render_str(self.title, style="rule.text")
        title_text.plain = title_text.plain.replace("\n", " ")
        title_text.expand_tabs()
        return title_text

    def _aligned_rule_text(
        self,
        title_text: Text,
        width: int,
        characters: str,
        chars_len: int,
        truncate_width: int,
    ) -> Text:
        rule_text = Text(end=self.end)
        if self.align == "center":
            return self._center_rule_text(
                rule_text, title_text, width, characters, chars_len, truncate_width
            )
        if self.align == "left":
            return self._left_rule_text(
                rule_text, title_text, width, characters, truncate_width
            )
        return self._right_rule_text(
            rule_text, title_text, width, characters, truncate_width
        )

    def _center_rule_text(
        self,
        rule_text: Text,
        title_text: Text,
        width: int,
        characters: str,
        chars_len: int,
        truncate_width: int,
    ) -> Text:
        title_text.truncate(truncate_width, overflow="ellipsis")
        side_width = (width - cell_len(title_text.plain)) // 2
        left = Text(characters * (side_width // chars_len + 1))
        left.truncate(side_width - 1)
        right_length = width - cell_len(left.plain) - cell_len(title_text.plain)
        right = Text(characters * (side_width // chars_len + 1))
        right.truncate(right_length)
        rule_text.append(left.plain + " ", self.style)
        rule_text.append(title_text)
        rule_text.append(" " + right.plain, self.style)
        rule_text.plain = set_cell_size(rule_text.plain, width)
        return rule_text

    def _left_rule_text(
        self,
        rule_text: Text,
        title_text: Text,
        width: int,
        characters: str,
        truncate_width: int,
    ) -> Text:
        title_text.truncate(truncate_width, overflow="ellipsis")
        rule_text.append(title_text)
        rule_text.append(" ")
        rule_text.append(characters * (width - rule_text.cell_len), self.style)
        rule_text.plain = set_cell_size(rule_text.plain, width)
        return rule_text

    def _right_rule_text(
        self,
        rule_text: Text,
        title_text: Text,
        width: int,
        characters: str,
        truncate_width: int,
    ) -> Text:
        title_text.truncate(truncate_width, overflow="ellipsis")
        rule_text.append(characters * (width - title_text.cell_len - 1), self.style)
        rule_text.append(" ")
        rule_text.append(title_text)
        rule_text.plain = set_cell_size(rule_text.plain, width)
        return rule_text

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = options.max_width
        characters = (
            "-"
            if (options.ascii_only and not self.characters.isascii())
            else self.characters
        )
        chars_len = cell_len(characters)
        if not self.title:
            yield self._rule_line(chars_len, width)
            return

        title_text = self._title_text(console)
        required_space = 4 if self.align == "center" else 2
        truncate_width = max(0, width - required_space)
        if not truncate_width:
            yield self._rule_line(chars_len, width)
            return

        yield self._aligned_rule_text(
            title_text, width, characters, chars_len, truncate_width
        )

    def _rule_line(self, chars_len: int, width: int) -> Text:
        rule_text = Text(self.characters * ((width // chars_len) + 1), self.style)
        rule_text.truncate(width)
        rule_text.plain = set_cell_size(rule_text.plain, width)
        return rule_text

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        return Measurement(1, 1)
