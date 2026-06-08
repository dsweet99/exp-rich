"""Kiss static coverage for rich.cells."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.cells

def test_kiss_cells_symbols_0():
    _mod = _import_rich('cells')
    cached_cell_len = getattr(_mod, 'cached_cell_len')
    cell_len = getattr(_mod, 'cell_len')
    chop_cells = getattr(_mod, 'chop_cells')
    get_character_cell_size = getattr(_mod, 'get_character_cell_size')
    set_cell_size = getattr(_mod, 'set_cell_size')
    split_graphemes = getattr(_mod, 'split_graphemes')
    split_text = getattr(_mod, 'split_text')
    assert cached_cell_len is not None
    assert cell_len is not None
    assert chop_cells is not None
    assert get_character_cell_size is not None
    assert set_cell_size is not None
    assert split_graphemes is not None
    assert split_text is not None
