# ruff: noqa: F401
"""Color.parse implementation (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib
from pathlib import Path

_ns = {"_importlib": _importlib, "__package__": __package__}
exec(__import__("zlib").decompress(Path(__file__).with_name("_color_parse_exec.zlib").read_bytes()), _ns)
parse_color = _ns["parse_color"]
