"""Padding type aliases (stdlib only, no rich imports)."""
from __future__ import annotations

from typing import Tuple, Union

PaddingDimensions = Union[int, Tuple[int], Tuple[int, int], Tuple[int, int, int, int]]
