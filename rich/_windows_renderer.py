from typing import Iterable

from ._win32_console import LegacyWindowsTerm
from ._windows_renderer_control import apply_control_codes
from ._segment_proxy import Segment


def legacy_windows_render(buffer: Iterable[Segment], term: LegacyWindowsTerm) -> None:
    """Makes appropriate Windows Console API calls based on the segments in the buffer.

    Args:
        buffer (Iterable[Segment]): Iterable of Segments to convert to Win32 API calls.
        term (LegacyWindowsTerm): Used to call the Windows Console API.
    """
    for text, style, control in buffer:
        if control:
            apply_control_codes(term, control)
            continue
        if style:
            term.write_styled(text, style)
        else:
            term.write_text(text)
