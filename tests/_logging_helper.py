"""Shared RichHandler test helper (isolates kiss dependency graph)."""
from __future__ import annotations

import importlib as _importlib

_Console = _importlib.import_module("rich._console_entry").Console
_RichHandler = _importlib.import_module("rich._logging_entry").RichHandler


def console_and_handler(**kwargs):
    handler_keys = (
        "enable_link_path",
        "rich_tracebacks",
        "markup",
        "tracebacks_extra_lines",
    )
    handler_kwargs = {k: kwargs.pop(k) for k in list(kwargs) if k in handler_keys}
    console = _Console(**kwargs)
    return console, _RichHandler(console=console, **handler_kwargs)
