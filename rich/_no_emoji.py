from typing import Literal

EmojiVariant = Literal["emoji", "text"]


class NoEmoji(Exception):
    """No emoji by that name."""
