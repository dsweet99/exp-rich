"""Tests for render factory registration."""
import pytest

import rich._render_factory as factory
from rich.containers import Renderables
from rich.table import Table


def test_table_grid_registered():
    factory.register_table_grid(Table.grid)
    grid = factory.table_grid(padding=(0, 1))
    assert grid.__class__.__name__ == "Table"


def test_renderables_registered():
    factory.register_renderables(Renderables)
    group = factory.renderables(["a"])
    assert isinstance(group, Renderables)


def test_table_grid_not_registered():
    old = factory._table_grid_factory
    factory._table_grid_factory = None
    try:
        with pytest.raises(RuntimeError, match="Table.grid factory not registered"):
            factory.table_grid()
    finally:
        factory._table_grid_factory = old


def test_renderables_not_registered():
    old = factory._renderables_factory
    factory._renderables_factory = None
    try:
        with pytest.raises(RuntimeError, match="Renderables class not registered"):
            factory.renderables(["a"])
    finally:
        factory._renderables_factory = old
