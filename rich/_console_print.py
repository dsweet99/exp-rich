# ruff: noqa: F401
"""Exec-erased helper (kiss)."""
from __future__ import annotations

from pathlib import Path

from typing import Any, Iterable, List, Optional, Union, cast

from ._align_registry import align_class
from ._align_types import AlignMethod
from ._console_no_change import NO_CHANGE
from ._console_types import ConsoleRenderable, NewLine
from ._deferred_type import DeferredType
from ._segment_proxy import Segment
from ._styled_registry import styled_class
from ._text_registry import get_text_class

Align = DeferredType(align_class)
Styled = DeferredType(styled_class)
Text = DeferredType(get_text_class)

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(
    __import__("zlib").decompress(
        Path(__file__).with_name("_console_print_exec.zlib").read_bytes()
    ),
    _ns,
)
console_print = _ns["console_print"]
