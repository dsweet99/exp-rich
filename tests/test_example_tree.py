"""Tests for examples.tree."""
from __future__ import annotations

import pathlib


def test_walk_directory_adds_children(tmp_path):
    from examples.tree import walk_directory
    from rich.tree import Tree

    (tmp_path / "a.txt").write_text("x")
    tree = Tree("root")
    walk_directory(pathlib.Path(tmp_path), tree)
    assert tree.children
