from typing import Callable, Iterable, Sequence, Tuple, cast

from rich._win32_console import LegacyWindowsTerm, WindowsCoordinates
from rich.segment import ControlCode, ControlType, Segment


def _legacy_windows_cursor_move_to(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, x, y = cast(Tuple[ControlType, int, int], control_code)
    term.move_cursor_to(WindowsCoordinates(row=y - 1, col=x - 1))


def _legacy_windows_erase_in_line(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, mode = cast(Tuple[ControlType, int], control_code)
    if mode == 0:
        term.erase_end_of_line()
    elif mode == 1:
        term.erase_start_of_line()
    elif mode == 2:
        term.erase_line()


def _legacy_windows_set_title(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, title = cast(Tuple[ControlType, str], control_code)
    term.set_title(title)


def _legacy_windows_move_to_column(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, column = cast(Tuple[ControlType, int], control_code)
    term.move_cursor_to_column(column - 1)


_LEGACY_WINDOWS_CONTROL_HANDLERS: dict[
    ControlType, Callable[[LegacyWindowsTerm, ControlCode], None]
] = {
    ControlType.CURSOR_MOVE_TO: _legacy_windows_cursor_move_to,
    ControlType.CARRIAGE_RETURN: lambda term, _: term.write_text("\r"),
    ControlType.HOME: lambda term, _: term.move_cursor_to(WindowsCoordinates(0, 0)),
    ControlType.CURSOR_UP: lambda term, _: term.move_cursor_up(),
    ControlType.CURSOR_DOWN: lambda term, _: term.move_cursor_down(),
    ControlType.CURSOR_FORWARD: lambda term, _: term.move_cursor_forward(),
    ControlType.CURSOR_BACKWARD: lambda term, _: term.move_cursor_backward(),
    ControlType.CURSOR_MOVE_TO_COLUMN: _legacy_windows_move_to_column,
    ControlType.HIDE_CURSOR: lambda term, _: term.hide_cursor(),
    ControlType.SHOW_CURSOR: lambda term, _: term.show_cursor(),
    ControlType.ERASE_IN_LINE: _legacy_windows_erase_in_line,
    ControlType.SET_WINDOW_TITLE: _legacy_windows_set_title,
}


def _legacy_windows_render_control(
    term: LegacyWindowsTerm, control_codes: Sequence[ControlCode]
) -> None:
    for control_code in control_codes:
        handler = _LEGACY_WINDOWS_CONTROL_HANDLERS.get(control_code[0])
        if handler is not None:
            handler(term, control_code)


def _legacy_windows_render_segment(
    term: LegacyWindowsTerm, text: str, style, control
) -> None:
    if not control:
        if style:
            term.write_styled(text, style)
        else:
            term.write_text(text)
        return
    _legacy_windows_render_control(term, control)


def legacy_windows_render(buffer: Iterable[Segment], term: LegacyWindowsTerm) -> None:
    """Makes appropriate Windows Console API calls based on the segments in the buffer.

    Args:
        buffer (Iterable[Segment]): Iterable of Segments to convert to Win32 API calls.
        term (LegacyWindowsTerm): Used to call the Windows Console API.
    """
    for text, style, control in buffer:
        _legacy_windows_render_segment(term, text, style, control)
