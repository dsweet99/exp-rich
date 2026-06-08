from __future__ import annotations

from ._lazy import import_attr
from typing import Iterable, Sequence, Tuple, cast

LegacyWindowsTerm = import_attr('rich._win32_console', 'LegacyWindowsTerm')
WindowsCoordinates = import_attr('rich._win32_console', 'WindowsCoordinates')
ControlCode = import_attr('rich.segment', 'ControlCode')
ControlType = import_attr('rich.segment', 'ControlType')
Segment = import_attr('rich.segment', 'Segment')


def _erase_in_line(term: LegacyWindowsTerm, mode: int) -> None:
    if mode == 0:
        term.erase_end_of_line()
    elif mode == 1:
        term.erase_start_of_line()
    elif mode == 2:
        term.erase_line()


def _apply_cursor_move_to(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, x, y = cast(Tuple[ControlType, int, int], control_code)
    term.move_cursor_to(WindowsCoordinates(row=y - 1, col=x - 1))


def _apply_cursor_move_to_column(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, column = cast(Tuple[ControlType, int], control_code)
    term.move_cursor_to_column(column - 1)


def _apply_set_window_title(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, title = cast(Tuple[ControlType, str], control_code)
    term.set_title(title)


def _apply_legacy_control(term: LegacyWindowsTerm, control_code: ControlCode) -> None:
    control_type = control_code[0]
    if control_type == ControlType.CURSOR_MOVE_TO:
        _apply_cursor_move_to(term, control_code)
    elif control_type == ControlType.CARRIAGE_RETURN:
        term.write_text("\r")
    elif control_type == ControlType.HOME:
        term.move_cursor_to(WindowsCoordinates(0, 0))
    elif control_type == ControlType.CURSOR_UP:
        term.move_cursor_up()
    elif control_type == ControlType.CURSOR_DOWN:
        term.move_cursor_down()
    elif control_type == ControlType.CURSOR_FORWARD:
        term.move_cursor_forward()
    elif control_type == ControlType.CURSOR_BACKWARD:
        term.move_cursor_backward()
    elif control_type == ControlType.CURSOR_MOVE_TO_COLUMN:
        _apply_cursor_move_to_column(term, control_code)
    elif control_type == ControlType.HIDE_CURSOR:
        term.hide_cursor()
    elif control_type == ControlType.SHOW_CURSOR:
        term.show_cursor()
    elif control_type == ControlType.ERASE_IN_LINE:
        _, mode = cast(Tuple[ControlType, int], control_code)
        _erase_in_line(term, mode)
    elif control_type == ControlType.SET_WINDOW_TITLE:
        _apply_set_window_title(term, control_code)


def _write_segment(
    term: LegacyWindowsTerm, text: str, style: object, control: object
) -> None:
    if not control:
        if style:
            term.write_styled(text, style)
        else:
            term.write_text(text)
        return
    for control_code in cast(Sequence[ControlCode], control):
        _apply_legacy_control(term, control_code)


def legacy_windows_render(buffer: Iterable[Segment], term: LegacyWindowsTerm) -> None:
    """Makes appropriate Windows Console API calls based on the segments in the buffer.

    Args:
        buffer (Iterable[Segment]): Iterable of Segments to convert to Win32 API calls.
        term (LegacyWindowsTerm): Used to call the Windows Console API.
    """
    for text, style, control in buffer:
        _write_segment(term, text, style, control)
