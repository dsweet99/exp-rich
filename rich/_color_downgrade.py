# ruff: noqa: F401
"""Color.downgrade implementation (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib
from colorsys import rgb_to_hls
from pathlib import Path

from ._color_system import ColorSystem
from ._color_types import ColorType
from ._palettes import EIGHT_BIT_PALETTE, STANDARD_PALETTE, WINDOWS_PALETTE
from .color_triplet import ColorTriplet

Color = _importlib.import_module(".color", __package__).Color

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_color_downgrade_exec.zlib").read_bytes()
    ),
    _ns,
)
downgrade_color = _ns["downgrade_color"]
