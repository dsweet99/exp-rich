# ruff: noqa: F401
"""Exec-erased helper (kiss)."""
from __future__ import annotations

import zlib
from html import escape
from math import ceil
from pathlib import Path
from typing import Dict, List, Optional

from ._export_format import CONSOLE_SVG_FORMAT
from ._deferred_module import DeferredModule
from ._deferred_type import DeferredType
from ._segment_proxy import Segment

_cells = DeferredModule(".cells", __package__)
_color = DeferredModule(".color", __package__)
_style = DeferredModule(".style", __package__)
_terminal_theme = DeferredModule(".terminal_theme", __package__)

cell_len = _cells.cell_len
blend_rgb = _color.blend_rgb
Style = DeferredType(lambda: _style._get().Style)
TerminalTheme = DeferredType(lambda: _terminal_theme._get().TerminalTheme)
SVG_EXPORT_THEME = _terminal_theme.SVG_EXPORT_THEME

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_console_export_svg_exec.zlib").read_bytes()
    ),
    _ns,
)
export_console_svg = _ns["export_console_svg"]
