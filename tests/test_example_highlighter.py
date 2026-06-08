"""Tests for examples.highlighter."""
from __future__ import annotations


def test_email_highlighter_styles_address():
    from examples.highlighter import EmailHighlighter
    from rich.text import Text

    hl = EmailHighlighter()
    text = Text("money@example.org")
    hl.highlight(text)
    assert text.plain
