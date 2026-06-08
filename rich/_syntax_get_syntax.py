# ruff: noqa: F401
"""Syntax._get_syntax implementation (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib
from pathlib import Path

from ._loop import loop_first
from ._segment_proxy import Segment
from .cells import cell_len
from .style import Style
from .text import Text

Lines = _importlib.import_module(".containers", __package__).Lines
Padding = _importlib.import_module(".padding", __package__).Padding
Comment = _importlib.import_module("pygments.token").Comment

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_syntax_get_syntax_exec.zlib").read_bytes()
    ),
    _ns,
)
get_syntax_segments = _ns["get_syntax_segments"]
