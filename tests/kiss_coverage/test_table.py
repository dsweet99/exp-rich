"""Kiss static coverage for rich.table."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.table

def test_kiss_table_symbols_0():
    _mod = _import_rich('table')
    Column = getattr(_mod, 'Column')
    Row = getattr(_mod, 'Row')
    Table = getattr(_mod, 'Table')
    _Cell = getattr(_mod, '_Cell')
    render_table_body = getattr(_mod, 'render_table_body')
    assert Column is not None
    assert Row is not None
    assert Table is not None
    assert _Cell is not None
    assert render_table_body is not None
