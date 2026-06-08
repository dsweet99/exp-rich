from __future__ import annotations

import sys
from typing import Optional, Union, TYPE_CHECKING

from ._emoji_replace import _emoji_replace
from ._emoji_types import EmojiVariant
from ._jupyter_mixin import JupyterMixin
from ._pick import M_SEGMENT, M_STYLE, rich_module

if TYPE_CHECKING:
    from ._types import ConsoleOptions, RenderResult, Style



def _Segment():
    return rich_module(M_SEGMENT).Segment


def _Style():
    return rich_module(M_STYLE).Style

NoEmoji = type(
    "NoEmoji",
    (Exception,),
    {"__doc__": "No emoji by that name."},
)

class Emoji(JupyterMixin):
    __slots__ = ["name", "style", "_char", "variant"]

    VARIANTS = {"text": "\ufe0e", "emoji": "\ufe0f"}

    def __init__(
        self,
        name: str,
        style: Union[str, "Style"] = "none",
        variant: Optional[EmojiVariant] = None,
    ) -> None:
        """A single emoji character.

        Args:
            name (str): Name of emoji.
            style (Union[str, Style], optional): Optional style. Defaults to None.

        Raises:
            NoEmoji: If the emoji doesn't exist.
        """
        from ._emoji_codes import EMOJI

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
        Segment = _Segment()
        yield Segment(self._char, console.get_style(self.style))

if __name__ == "__main__":  # pragma: no cover
    import importlib
    import sys

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    Console = importlib.import_module(_pkg + ".console").Console
    Columns = importlib.import_module(_pkg + ".columns").Columns

    console = Console(record=True)

    from ._emoji_codes import EMOJI

    columns = Columns(
        (f":{name}: {name}" for name in sorted(EMOJI.keys()) if "\u200d" not in name),
        column_first=True,
    )

    console.print(columns)
    if len(sys.argv) > 1:
        console.save_html(sys.argv[1])