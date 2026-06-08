"""Tests for Windows renderer control dispatch."""
from __future__ import annotations

from unittest.mock import MagicMock, call

from rich._windows_renderer_control import apply_control_codes
from rich.segment import ControlType


def test_apply_control_codes_dispatches_known_handlers() -> None:
    term = MagicMock()
    control_codes = [
        (ControlType.CARRIAGE_RETURN,),
        (ControlType.CURSOR_UP,),
        (ControlType.HIDE_CURSOR,),
        (ControlType.SHOW_CURSOR,),
        (ControlType.SET_WINDOW_TITLE, "title"),
    ]

    apply_control_codes(term, control_codes)

    assert term.write_text.call_args_list == [call("\r")]
    term.move_cursor_up.assert_called_once_with()
    term.hide_cursor.assert_called_once_with()
    term.show_cursor.assert_called_once_with()
    term.set_title.assert_called_once_with("title")


def test_apply_control_codes_ignores_unknown_control_type() -> None:
    term = MagicMock()
    unknown = (999,)  # type: ignore[tuple-item]

    apply_control_codes(term, [unknown])

    term.assert_not_called()
