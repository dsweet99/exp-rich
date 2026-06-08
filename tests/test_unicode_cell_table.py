"""Tests for the unicode CellTable definition module."""

from __future__ import annotations

from rich._unicode_data._cell_table import CellTable

CellTable


def test_unicode_cell_table_named_tuple():
    table = CellTable("17.0.0", ((0, 0, 0),), frozenset())
    assert table.unicode_version == "17.0.0"
