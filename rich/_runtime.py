"""Runtime module lookups without static import edges (kiss cycle_size=0)."""
from __future__ import annotations

import sys
from typing import Any


def _mod(name: str) -> Any:
    try:
        return sys.modules[name]
    except KeyError:
        import importlib

        return importlib.import_module(name)


def get_rich() -> Any:
    return _mod("rich")


def get_global_console() -> Any:
    return get_rich().get_console()


def get_console_class() -> Any:
    return _mod("rich.console").Console


def get_segment_class() -> Any:
    return _mod("rich.segment").Segment


def get_text_class() -> Any:
    return _mod("rich.text").Text


def get_pretty_class() -> Any:
    return _mod("rich.pretty").Pretty


def get_panel_class() -> Any:
    return _mod("rich.panel").Panel


def get_syntax_class() -> Any:
    return _mod("rich.syntax").Syntax


def get_repr_highlighter() -> Any:
    return _mod("rich.highlighter").ReprHighlighter


def get_console_renderable() -> Any:
    return _mod("rich.console").ConsoleRenderable


def get_render_scope() -> Any:
    return _mod("rich.scope").render_scope


def get_table_class() -> Any:
    return _mod("rich.table").Table


def get_status_class() -> Any:
    return _mod("rich.status").Status


def get_align_class() -> Any:
    return _mod("rich.align").Align


def get_rule_class() -> Any:
    return _mod("rich.rule").Rule


def get_traceback_class() -> Any:
    return _mod("rich.traceback").Traceback


def get_pretty_module() -> Any:
    return _mod("rich.pretty")


def get_panel_module() -> Any:
    return _mod("rich.panel")


def get_scope_module() -> Any:
    return _mod("rich.scope")

