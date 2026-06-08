"""Tests for rich._no_emoji."""

from __future__ import annotations

import pytest

from rich._no_emoji import EmojiVariant, NoEmoji

NoEmoji
EmojiVariant


def test_no_emoji_exception():
    with pytest.raises(NoEmoji):
        raise NoEmoji("unknown")
