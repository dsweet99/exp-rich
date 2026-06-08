"""Tests for examples.columns."""
from __future__ import annotations


def test_get_content_formats_user():
    from examples.columns import get_content

    user = {
        "name": {"first": "Ada", "last": "Lovelace"},
        "location": {"country": "UK"},
    }
    content = get_content(user)
    assert "Ada Lovelace" in content
    assert "UK" in content
