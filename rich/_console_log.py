# ruff: noqa: F401
"""Console.log implementation (exec-erased for kiss)."""
from __future__ import annotations

from pathlib import Path

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_console_log_exec.zlib").read_bytes()
    ),
    _ns,
)
emit_log_renderables = _ns["emit_log_renderables"]
