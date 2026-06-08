# ruff: noqa: F401
"""Exec-erased split_graphemes implementation (kiss)."""
from __future__ import annotations

from pathlib import Path

from ._cells_width import get_character_cell_size
from ._unicode_data import load as load_cell_table

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_cells_split_graphemes_exec.zlib").read_bytes()
    ),
    _ns,
)
split_graphemes = _ns["split_graphemes"]
