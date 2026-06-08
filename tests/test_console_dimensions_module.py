"""Tests for rich._console_dimensions."""

from __future__ import annotations

from rich._console_dimensions import ConsoleDimensions

ConsoleDimensions


def test_console_dimensions_fields():
    dims = ConsoleDimensions(80, 24)
    assert dims.width == 80
    assert dims.height == 24
