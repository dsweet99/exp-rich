"""Tests for examples.group2."""
from __future__ import annotations


def test_get_panels_yields_renderables():
    from examples.group2 import get_panels

    group = get_panels()
    assert group.renderables
