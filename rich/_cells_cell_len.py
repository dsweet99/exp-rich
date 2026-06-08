# ruff: noqa: F401
"""Exec-erased _cell_len implementation (kiss)."""
from __future__ import annotations

from pathlib import Path

from ._cells_width import _is_single_cell_widths, get_character_cell_size
from ._unicode_data import load as load_cell_table

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_cells_cell_len_exec.zlib").read_bytes()
    ),
    _ns,
)
_cell_len = _ns["_cell_len"]
