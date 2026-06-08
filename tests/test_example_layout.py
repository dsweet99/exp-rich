"""Tests for examples.layout."""
from __future__ import annotations


def test_clock_renders_time():
    import rich.highlighter  # noqa: F401 — register highlighter for layout import
    from examples.layout import Clock

    clock = Clock()
    assert clock.__rich__().plain
