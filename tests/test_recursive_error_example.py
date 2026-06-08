"""Tests for the recursive_error example script."""

from __future__ import annotations

import pytest

from examples.recursive_error import recursive_demo_bar, recursive_demo_foo

recursive_demo_foo
recursive_demo_bar


def test_recursive_error_raises_recursion_error():
    with pytest.raises(RecursionError):
        recursive_demo_foo(1)


def test_recursive_error_bar_is_callable():
    assert callable(recursive_demo_bar)
