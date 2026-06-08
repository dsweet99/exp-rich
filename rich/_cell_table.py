from __future__ import annotations

from typing import NamedTuple, Sequence


class CellTable(NamedTuple):
    """Contains unicode data required to measure the cell widths of glyphs."""

    unicode_version: str
    widths: Sequence[tuple[int, int, int]]
    narrow_to_wide: frozenset[str]
