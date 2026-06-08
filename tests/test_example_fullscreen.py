"""Tests for examples.fullscreen."""
from __future__ import annotations


def test_fullscreen_helpers():
    import rich.highlighter  # noqa: F401 — register highlighter for layout import
    from examples.fullscreen import Header, make_layout, make_sponsor_message, make_syntax

    assert make_layout() is not None
    make_sponsor_message()
    Header()
    make_syntax()
