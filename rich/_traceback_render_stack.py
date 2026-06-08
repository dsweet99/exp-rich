# ruff: noqa: F401
"""Traceback._render_stack implementation (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib
import linecache
import os
from pathlib import Path

from ._highlighter_registry import path_highlighter_class
from ._traceback_syntax_lines import iter_syntax_lines as _iter_syntax_lines
from ._traceback_types import Frame, Stack
from .scope import render_scope
from .text import Text

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_traceback_render_stack_exec.zlib").read_bytes()
    ),
    _ns,
)
render_traceback_stack = _ns["render_traceback_stack"]
