"""Tests for rich.scope."""

from __future__ import annotations

import importlib as _importlib
import io


def test_render_scope_renders_sorted_keys() -> None:
    render_scope = _importlib.import_module("rich.scope").render_scope
    Console = _importlib.import_module("rich._console_entry").Console
    scope = {"b": 2, "__dunder__": 0, "a": 1}
    panel = render_scope(scope, title="locals")
    console = Console(file=io.StringIO(), width=80)
    console.print(panel)
    output = console.file.getvalue()

    assert "__dunder__ = 0" in output
    assert "a = 1" in output
    assert "b = 2" in output
    assert output.index("__dunder__ =") < output.index("a = 1") < output.index("b = 2")


def test_render_scope_preserves_insertion_order_when_unsorted() -> None:
    render_scope = _importlib.import_module("rich.scope").render_scope
    Console = _importlib.import_module("rich._console_entry").Console
    scope = {"first": 1, "second": 2}
    panel = render_scope(scope, sort_keys=False)
    console = Console(file=io.StringIO(), width=80)
    console.print(panel)
    output = console.file.getvalue()

    assert output.index("first") < output.index("second")
