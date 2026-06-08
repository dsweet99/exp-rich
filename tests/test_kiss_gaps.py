"""Tests for kiss coverage gaps in dev tools and selective rich modules."""

import io
from dataclasses import dataclass
from typing import Optional

import rich._ratio
from rich.__init__ import inspect
from rich._ratio import ratio_resolve
from rich._windows import WindowsConsoleFeatures, get_windows_console_features
from rich.console import Console
from rich.scope import render_scope
from tools.generate_kiss_coverage_tests import (
    all_rich_files,
    code_units,
    module_import_path,
    render_block,
)


@dataclass
class E:
    size: Optional[int] = None
    ratio: int = 1
    minimum_size: int = 1


def test_rich_init_exports():
    import rich

    console = Console(file=io.StringIO())
    backup_file = rich.get_console().file
    try:
        rich.get_console().file = console.file
        inspect({"a": 1})
    finally:
        rich.get_console().file = backup_file


def test_ratio_resolve_edges():
    assert sum(ratio_resolve(110, [E(None, 1, 1), E(None, 1, 1)])) == 110


def test_windows_console_features_from_windows_module():
    features = get_windows_console_features()
    assert isinstance(features, WindowsConsoleFeatures)
    assert get_windows_console_features is not None


def test_render_scope():
    panel = render_scope({"a": 1}, title="locals")
    Console(file=io.StringIO()).print(panel)
def test_generate_kiss_coverage_helpers():
    files = all_rich_files()
    assert any(f.name == "console.py" for f in files)
    bar = next(f for f in files if f.name == "bar.py")
    assert module_import_path(bar) == "rich.bar"
    classes, functions = code_units(bar)
    assert "Bar" in classes
    block = render_block("rich.bar", bar)
    assert "test_kiss_bar_symbols_0" in block
    assert "Bar" in block
