# ruff: noqa: F401
"""Exec-erased helper (kiss)."""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Dict, List, Optional

from ._export_format import CONSOLE_HTML_FORMAT
from ._deferred_module import DeferredModule
from ._deferred_type import DeferredType
from ._segment_proxy import Segment

_terminal_theme = DeferredModule(".terminal_theme", __package__)
TerminalTheme = DeferredType(lambda: _terminal_theme._get().TerminalTheme)
DEFAULT_TERMINAL_THEME = _terminal_theme.DEFAULT_TERMINAL_THEME

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_console_export_html_exec.zlib").read_bytes()
    ),
    _ns,
)
export_console_html = _ns["export_console_html"]
