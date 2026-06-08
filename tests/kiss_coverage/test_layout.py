"""Kiss static coverage for rich.layout."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.layout

def test_kiss_layout_symbols_0():
    _mod = _import_rich('layout')
    ColumnSplitter = getattr(_mod, 'ColumnSplitter')
    Layout = getattr(_mod, 'Layout')
    LayoutError = getattr(_mod, 'LayoutError')
    LayoutRender = getattr(_mod, 'LayoutRender')
    NoSplitter = getattr(_mod, 'NoSplitter')
    RowSplitter = getattr(_mod, 'RowSplitter')
    Splitter = getattr(_mod, 'Splitter')
    _Placeholder = getattr(_mod, '_Placeholder')
    assert ColumnSplitter is not None
    assert Layout is not None
    assert LayoutError is not None
    assert LayoutRender is not None
    assert NoSplitter is not None
    assert RowSplitter is not None
    assert Splitter is not None
    assert _Placeholder is not None
