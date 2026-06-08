from __future__ import annotations

from ._lazy import import_attr
import sys
from typing import TYPE_CHECKING, Literal, Optional, Union

_emoji_replace = import_attr('rich._emoji_replace', '_emoji_replace')
JupyterMixin = import_attr('rich.jupyter', 'JupyterMixin')
Segment = import_attr('rich.segment', 'Segment')
Style = import_attr('rich.style', 'Style')



EmojiVariant = Literal["emoji", "text"]
if TYPE_CHECKING:
    from .console import Console, ConsoleOptions, RenderResult



class NoEmoji(Exception):
    """No emoji by that name."""


class Emoji(JupyterMixin):
    __slots__ = ["name", "style", "_char", "variant"]

    VARIANTS = {"text": "\ufe0e", "emoji": "\ufe0f"}

    def __init__(
        self,
        name: str,
        style: Union[str, Style] = "none",
        variant: Optional[EmojiVariant] = None,
    ) -> None:
        """A single emoji character.

        Args:
            name (str): Name of emoji.
            style (Union[str, Style], optional): Optional style. Defaults to None.

        Raises:
            NoEmoji: If the emoji doesn't exist.
        """
        EMOJI = import_attr('rich._emoji_codes', 'EMOJI')

        self.name = name
        self.style = style
        self.variant = variant
        try:
            self._char = EMOJI[name]
        except KeyError:
            raise NoEmoji(f"No emoji called {name!r}")
        if variant is not None:
            self._char += self.VARIANTS.get(variant, "")

    @classmethod
    def replace(cls, text: str) -> str:
        """Replace emoji markup with corresponding unicode characters.

        Args:
            text (str): A string with emojis codes, e.g. "Hello :smiley:!"

        Returns:
            str: A string with emoji codes replaces with actual emoji.
        """
        return _emoji_replace(text)

    def __repr__(self) -> str:
        return f"<emoji {self.name!r}>"

    def __str__(self) -> str:
        return self._char

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield Segment(self._char, console.get_style(self.style))


if __name__ == "__main__":  # pragma: no cover
    import sys

    Columns = import_attr('rich.columns', 'Columns')
    Console = import_attr('rich.console', 'Console')

    console = Console(record=True)

    EMOJI = import_attr('rich._emoji_codes', 'EMOJI')

    columns = Columns(
        (f":{name}: {name}" for name in sorted(EMOJI.keys()) if "\u200d" not in name),
        column_first=True,
    )

    console.print(columns)
    if len(sys.argv) > 1:
        console.save_html(sys.argv[1])
