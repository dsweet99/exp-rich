from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional, Sequence, Tuple, cast

from ._pick import M_SEGMENT, M_WIN32_CONSOLE, rich_module


def _segment_module():
    return rich_module(M_SEGMENT)


def _win32_module():
    return rich_module(M_WIN32_CONSOLE)


ControlCode = _segment_module().ControlCode
ControlType = _segment_module().ControlType
Segment = _segment_module().Segment
LegacyWindowsTerm = _win32_module().LegacyWindowsTerm
WindowsCoordinates = _win32_module().WindowsCoordinates

_ControlHandler = Callable[[LegacyWindowsTerm, ControlCode], None]


def _legacy_windows_cursor_move_to(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, x, y = cast(Tuple[ControlType, int, int], control_code)
    term.move_cursor_to(WindowsCoordinates(row=y - 1, col=x - 1))


def _legacy_windows_erase_in_line(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    _, mode = cast(Tuple[ControlType, int], control_code)
    erase = {0: term.erase_end_of_line, 1: term.erase_start_of_line, 2: term.erase_line}
    handler = erase.get(mode)
    if handler is not None:
        handler()


_LEGACY_WINDOWS_CONTROL_HANDLERS: Dict[ControlType, _ControlHandler] = {
    ControlType.CURSOR_MOVE_TO: _legacy_windows_cursor_move_to,
    ControlType.CARRIAGE_RETURN: lambda term, _code: term.write_text("\r"),
    ControlType.HOME: lambda term, _code: term.move_cursor_to(WindowsCoordinates(0, 0)),
    ControlType.CURSOR_UP: lambda term, _code: term.move_cursor_up(),
    ControlType.CURSOR_DOWN: lambda term, _code: term.move_cursor_down(),
    ControlType.CURSOR_FORWARD: lambda term, _code: term.move_cursor_forward(),
    ControlType.CURSOR_BACKWARD: lambda term, _code: term.move_cursor_backward(),
    ControlType.CURSOR_MOVE_TO_COLUMN: lambda term, code: term.move_cursor_to_column(
        cast(Tuple[ControlType, int], code)[1] - 1
    ),
    ControlType.HIDE_CURSOR: lambda term, _code: term.hide_cursor(),
    ControlType.SHOW_CURSOR: lambda term, _code: term.show_cursor(),
    ControlType.ERASE_IN_LINE: _legacy_windows_erase_in_line,
    ControlType.SET_WINDOW_TITLE: lambda term, code: term.set_title(
        cast(Tuple[ControlType, str], code)[1]
    ),
}


def _legacy_windows_apply_control(
    term: LegacyWindowsTerm, control_code: ControlCode
) -> None:
    """Apply a single control code to the legacy Windows terminal."""
    handler = _LEGACY_WINDOWS_CONTROL_HANDLERS.get(control_code[0])
    if handler is not None:
        handler(term, control_code)


def _legacy_windows_render_segment(
    term: LegacyWindowsTerm,
    text: str,
    style: Optional[object],
    control: Optional[Sequence[ControlCode]],
) -> None:
    """Render a single segment to the legacy Windows terminal."""
    if not control:
        if style:
            term.write_styled(text, style)
        else:
            term.write_text(text)
        return
    for control_code in control:
        _legacy_windows_apply_control(term, control_code)


def legacy_windows_render(buffer: Iterable[Segment], term: LegacyWindowsTerm) -> None:
    """Makes appropriate Windows Console API calls based on the segments in the buffer.

    Args:
        buffer (Iterable[Segment]): Iterable of Segments to convert to Win32 API calls.
        term (LegacyWindowsTerm): Used to call the Windows Console API.
    """
    for text, style, control in buffer:
        _legacy_windows_render_segment(term, text, style, control)
