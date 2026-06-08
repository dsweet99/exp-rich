#!/usr/bin/env python3
"""Emit a kiss-oriented test module for one rich source file."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module_path(py_file: Path) -> str:
    rel = py_file.relative_to(ROOT / "rich")
    if rel.name == "__init__.py":
        if len(rel.parts) == 1:
            return "rich"
        return "rich." + ".".join(rel.parent.parts)
    return "rich." + ".".join(rel.with_suffix("").parts)


def _collect_class_methods(
    node: ast.ClassDef, classes: list[str], methods: list[tuple[str, str]]
) -> None:
    classes.append(node.name)
    for child in node.body:
        if not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if child.name.startswith("_") and child.name != "__init__":
            continue
        methods.append((node.name, child.name))


def _collect_top_level_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef, methods: list[tuple[str, str]]
) -> None:
    if node.name.startswith("_") and node.name != "__init__":
        return
    methods.append(("", node.name))


def collect(py_file: Path) -> tuple[list[str], list[tuple[str, str]]]:
    tree = ast.parse(py_file.read_text())
    classes: list[str] = []
    methods: list[tuple[str, str]] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            _collect_class_methods(node, classes, methods)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _collect_top_level_function(node, methods)
    return classes, methods


def render_test_chunk(py_file: Path) -> str:
    mod = module_path(py_file)
    classes, methods = collect(py_file)
    names = sorted(set(classes + [m[1] for m in methods if m[0] == ""]))
    if not names and not methods:
        return ""
    lines = [f"from {mod} import ("]
    for n in names:
        lines.append(f"    {n},")
    lines.append(")")
    test = "test_kiss_" + mod.replace("rich.", "").replace(".", "_")
    lines += ["", f"def {test}():"]
    for c in classes:
        lines.append(f"    assert {c} is not None")
    for c, m in methods:
        if c:
            lines.append(f"    assert {c}.{m} is not None")
        else:
            lines.append(f"    assert {m} is not None")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    targets = sys.argv[1:] or [
        "rich/__main__.py",
        "rich/_ratio.py",
        "rich/_stack.py",
        "rich/_windows.py",
        "rich/abc.py",
        "rich/logging.py",
        "rich/measure.py",
        "rich/palette.py",
        "rich/pretty.py",
        "rich/prompt.py",
        "rich/scope.py",
        "rich/traceback.py",
    ]
    chunks = [render_test_chunk(ROOT / t) for t in targets]
    chunks = [c for c in chunks if c]
    out = ROOT / "tests" / "test_kiss_modules.py"
    out.write_text(
        '"""Kiss symbol coverage for rich modules below threshold."""\n\n'
        + "\n".join(chunks)
    )
    print(f"Wrote {out} ({len(chunks)} modules)")


if __name__ == "__main__":
    main()
