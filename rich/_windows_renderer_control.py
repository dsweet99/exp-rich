"""Control-code dispatch for legacy Windows rendering."""
from __future__ import annotations

from typing import Any, Callable, Sequence, Tuple, cast

from ._segment_aux import ControlCode, ControlType


def _move_cursor_to(term: Any, control_code: ControlCode) -> None:
    from ._win32_console import WindowsCoordinates

    _, x, y = cast(Tuple[ControlType, int, int], control_code)
    term.move_cursor_to(WindowsCoordinates(row=y - 1, col=x - 1))


def _erase_in_line(term: Any, control_code: ControlCode) -> None:
    _, mode = cast(Tuple[ControlType, int], control_code)
    if mode == 0:
        term.erase_end_of_line()
    elif mode == 1:
        term.erase_start_of_line()
    elif mode == 2:
        term.erase_line()


def _set_window_title(term: Any, control_code: ControlCode) -> None:
    _, title = cast(Tuple[ControlType, str], control_code)
    term.set_title(title)


def _move_cursor_to_column(term: Any, control_code: ControlCode) -> None:
    _, column = cast(Tuple[ControlType, int], control_code)
    term.move_cursor_to_column(column - 1)


def _move_home(term: Any, _: ControlCode) -> None:
    from ._win32_console import WindowsCoordinates

    term.move_cursor_to(WindowsCoordinates(0, 0))


_CONTROL_HANDLERS: dict[
    ControlType, Callable[[Any, ControlCode], None]
] = {
    ControlType.CURSOR_MOVE_TO: _move_cursor_to,
    ControlType.CARRIAGE_RETURN: lambda term, _: term.write_text("\r"),
    ControlType.HOME: _move_home,
    ControlType.CURSOR_UP: lambda term, _: term.move_cursor_up(),
    ControlType.CURSOR_DOWN: lambda term, _: term.move_cursor_down(),
    ControlType.CURSOR_FORWARD: lambda term, _: term.move_cursor_forward(),
    ControlType.CURSOR_BACKWARD: lambda term, _: term.move_cursor_backward(),
    ControlType.CURSOR_MOVE_TO_COLUMN: _move_cursor_to_column,
    ControlType.HIDE_CURSOR: lambda term, _: term.hide_cursor(),
    ControlType.SHOW_CURSOR: lambda term, _: term.show_cursor(),
    ControlType.ERASE_IN_LINE: _erase_in_line,
    ControlType.SET_WINDOW_TITLE: _set_window_title,
}


def apply_control_codes(term: Any, control_codes: Sequence[ControlCode]) -> None:
    """Apply a sequence of control codes to the Windows terminal."""
    for control_code in control_codes:
        handler = _CONTROL_HANDLERS.get(control_code[0])
        if handler is not None:
            handler(term, control_code)
