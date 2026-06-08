"""Kiss static coverage for rich.emoji."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.emoji

def test_kiss_emoji_symbols_0():
    _mod = _import_rich('emoji')
    Emoji = getattr(_mod, 'Emoji')
    NoEmoji = getattr(_mod, 'NoEmoji')
    assert Emoji is not None
    assert NoEmoji is not None
