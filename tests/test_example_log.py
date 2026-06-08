"""Tests for examples.log."""
from __future__ import annotations


def test_request_highlighter_parses_http_line():
    from examples.log import RequestHighlighter
    from rich.text import Text

    hl = RequestHighlighter()
    text = Text("HTTP GET /path HTTP/1.1")
    hl.highlight(text)
