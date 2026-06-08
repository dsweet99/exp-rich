"""Tests for table init helper coverage."""
from __future__ import annotations


def test_table_constructor_initializes_via_helper():
    from rich._table_init import init_table_state
    from rich.table import Table

    table = Table("name", "value", title="demo", width=30, highlight=True)
    assert init_table_state is not None

    assert table.title == "demo"
    assert table.width == 30
    assert table.highlight is True
    assert len(table.columns) == 2
    assert table.columns[0].header == "name"
