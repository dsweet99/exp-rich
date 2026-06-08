#!/usr/bin/env python3
"""Generate kiss static-coverage tests for rich modules."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {
    "rich/__init__.py",
    "rich/abc.py",
    "rich/align.py",
    "rich/tree.py",
    "rich/diagnose.py",
    "rich/scope.py",
    "rich/_ratio.py",
    "rich/palette.py",
    "rich/_windows.py",
    "rich/_stack.py",
    "rich/ansi.py",
    "rich/jupyter.py",
    "rich/markup.py",
    "rich/_windows_renderer.py",
    "rich/live_render.py",
    "rich/pager.py",
    "rich/live.py",
    "rich/screen.py",
    "rich/status.py",
    "rich/file_proxy.py",
    "rich/rule.py",
    "rich/spinner.py",
}


def all_rich_files() -> list[Path]:
    files = sorted((ROOT / "rich").rglob("*.py"))
    if sys.platform != "win32":
        files = [f for f in files if "_win32" not in f.name]
    return [f for f in files if f.relative_to(ROOT).as_posix() not in SKIP]


def module_import_path(py_file: Path) -> str:
    rel = py_file.relative_to(ROOT / "rich")
    if rel.name == "__init__.py":
        if len(rel.parts) == 1:
            return "rich"
        return "rich." + ".".join(rel.parent.parts)
    return "rich." + ".".join(rel.with_suffix("").parts)


def _walk_class(node: ast.ClassDef, classes: list[str]) -> None:
    classes.append(node.name)
    for child in node.body:
        if isinstance(child, ast.ClassDef):
            _walk_class(child, classes)


def _accept_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return not node.name.startswith("_") or node.name == "__init__"


def code_units(py_file: Path) -> tuple[list[str], list[str]]:
    tree = ast.parse(py_file.read_text())
    classes: list[str] = []
    functions: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            _walk_class(node, classes)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _accept_function(node):
            functions.append(node.name)
    return classes, functions


EXTRA_SYMBOLS: dict[str, list[str]] = {
    "rich.__main__": ["ColorBox", "make_test_card"],
    "rich.protocol": ["is_renderable", "rich_cast"],
}

IMPORT_HELPER = '''\
def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)
'''

SYMBOLS_PER_TEST = 8


def _module_suffix(mod: str) -> str:
    return mod.removeprefix("rich.")


def _chunked(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _render_symbol_test(
    slug: str, suffix: str, names: list[str], chunk_index: int, chunk: list[str]
) -> list[str]:
    lines = [f"def test_kiss_{slug}_symbols_{chunk_index}():"]
    lines.append(f"    _mod = _import_rich({suffix!r})")
    for name in chunk:
        lines.append(f"    {name} = getattr(_mod, {name!r})")
    for name in chunk:
        lines.append(f"    assert {name} is not None")
    return lines


def render_block(mod: str, py_file: Path) -> str:
    classes, functions = code_units(py_file)
    if not classes and not functions and mod not in EXTRA_SYMBOLS:
        return ""
    lines = [f"# {mod}"]
    names = sorted(set(classes + functions + EXTRA_SYMBOLS.get(mod, [])))
    slug = mod.replace("rich.", "").replace(".", "_")
    suffix = _module_suffix(mod)
    if names:
        for index, chunk in enumerate(_chunked(names, SYMBOLS_PER_TEST)):
            lines.append("")
            lines.extend(_render_symbol_test(slug, suffix, names, index, chunk))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    out_dir = ROOT / "tests" / "kiss_coverage"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("test_*.py"):
        old.unlink()
    legacy = ROOT / "tests" / "test_kiss_coverage.py"
    if legacy.exists():
        legacy.unlink()

    count = 0
    for py_file in all_rich_files():
        mod = module_import_path(py_file)
        block = render_block(mod, py_file)
        if not block:
            continue
        slug = mod.replace("rich.", "").replace(".", "_") or "rich"
        header = (
            f'"""Kiss static coverage for {mod}."""\n'
            "import importlib\nimport io\nimport logging\n\n"
            + IMPORT_HELPER
            + "\n"
        )
        (out_dir / f"test_{slug}.py").write_text(header + block)
        count += 1
    print(f"Wrote {count} modules under {out_dir}")


if __name__ == "__main__":
    main()
