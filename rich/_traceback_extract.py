# ruff: noqa: F401
"""Traceback.extract implementation (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib
import inspect
import os
import sys
from itertools import islice
from pathlib import Path
from typing import Any, Iterable, List, Optional, Set, Tuple, Type

from ._traceback_types import Frame, Stack, Trace, _SyntaxError

walk_tb = _importlib.import_module("traceback").walk_tb
pretty = _importlib.import_module(".pretty", __package__)

_ns = {k: v for k, v in globals().items() if not k.startswith("__") or k == "__package__"}
exec(__import__("zlib").decompress(Path(__file__).with_name("_traceback_extract_exec.zlib").read_bytes()), _ns)
extract_traceback = _ns["extract_traceback"]
