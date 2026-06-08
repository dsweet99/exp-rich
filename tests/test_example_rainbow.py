"""Tests for examples.rainbow."""
from __future__ import annotations


def test_rainbow_highlighter_colors_text():
    from examples.rainbow import RainbowHighlighter
    from rich.text import Text

    hl = RainbowHighlighter()
    text = Text("hello")
    hl.highlight(text)
