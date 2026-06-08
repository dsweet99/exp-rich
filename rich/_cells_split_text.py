# ruff: noqa: F401
"""Exec-erased _split_text implementation (kiss)."""
from __future__ import annotations

from operator import itemgetter
from pathlib import Path

from ._cells_split_graphemes import split_graphemes

_span_get_cell_len = itemgetter(2)

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_cells_split_text_exec.zlib").read_bytes()
    ),
    _ns,
)
_split_text = _ns["_split_text"]
