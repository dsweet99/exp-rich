"""Tests for rich._console_no_change."""

from __future__ import annotations

from rich._console_no_change import NO_CHANGE, NoChange

NoChange
NO_CHANGE


def test_no_change_sentinel_is_singleton():
    assert isinstance(NO_CHANGE, NoChange)
    assert NoChange() is not NO_CHANGE
