"""Kiss static coverage for rich._cell_table."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._cell_table

def test_kiss__cell_table_symbols_0():
    _mod = _import_rich('_cell_table')
    CellTable = getattr(_mod, 'CellTable')
    assert CellTable is not None
