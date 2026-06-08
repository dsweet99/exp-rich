"""Tests for examples.listdir."""
from __future__ import annotations


def test_make_filename_text_includes_name(tmp_path):
    from examples.listdir import make_filename_text

    path = tmp_path / "foo.py"
    path.write_text("x")
    text = make_filename_text(str(tmp_path), "foo.py")
    assert "foo.py" in text.plain
