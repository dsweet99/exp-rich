"""Tests for examples.exception."""
from __future__ import annotations


def test_divide_by_returns_quotient():
    from examples.exception import divide_by

    assert divide_by(10, 2) == 5


def test_divide_all_handles_zero_divisor():
    from examples.exception import divide_all

    divide_all([(1, 1), (1, 0)])
