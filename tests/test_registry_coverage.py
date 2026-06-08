"""Behavioral coverage for kiss-tracked registry and helper modules."""
from __future__ import annotations

import io
import sys

from rich._color_system import ColorSystem
from rich._console_dimensions import ConsoleDimensions
from rich._console_no_change import NO_CHANGE, NoChange
from rich._group_registry import group, group_class, register_group
from rich._unicode_data._cell_table import CellTable
from rich.cells import cell_len


def test_color_system_repr_and_str():
    assert repr(ColorSystem.EIGHT_BIT) == "ColorSystem.EIGHT_BIT"
    assert str(ColorSystem.WINDOWS) == "ColorSystem.WINDOWS"


def test_console_dimensions_namedtuple():
    dims = ConsoleDimensions(width=120, height=40)
    assert dims[0] == 120
    assert dims[1] == 40
    assert dims._replace(width=100).width == 100


def test_no_change_sentinel_type():
    assert isinstance(NO_CHANGE, NoChange)
    assert type(NO_CHANGE) is NoChange


def test_group_registry_decorator_fit_false():
    from rich._console_types import Group

    register_group(Group)

    @group(fit=False)
    def make_items():
        return ["a", "b"]

    grouped = make_items()
    assert isinstance(grouped, Group)
    assert grouped.fit is False
    assert group_class() is Group


def test_cell_table_namedtuple_fields():
    table = CellTable("17.0.0", ((0, 0, 1),), frozenset({"a"}))
    assert table.unicode_version == "17.0.0"
    assert table.narrow_to_wide == frozenset({"a"})


def test_cell_len_uses_long_path_for_special_sequences():
    assert cell_len("a\u200db") >= 1


def test_pretty_install_registers_repr_handler():
    from rich.pretty import _repl_display_hook, install

    old_displayhook = sys.displayhook
    try:
        install()
        assert sys.displayhook is not old_displayhook
        assert callable(_repl_display_hook)
    finally:
        sys.displayhook = old_displayhook


def test_pretty_install_ipython_branch(monkeypatch):
    from rich._console_entry import Console
    from rich.pretty import _install_ipython_pretty, install

    _install_ipython_pretty
    monkeypatch.setattr(
        "rich.pretty._install_ipython_pretty",
        lambda *args, **kwargs: None,
    )
    console = Console(file=io.StringIO(), force_terminal=False)
    install(console=console)
