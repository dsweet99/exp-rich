"""Tests for developer tooling modules."""


def test_make_width_tables_is_script() -> None:
    """Width table generator exists as a build script."""
    from pathlib import Path

    path = Path(__file__).resolve().parent.parent / "tools" / "make_width_tables.py"
    assert path.is_file()
    source = path.read_text()
    assert "CellTable" in source
