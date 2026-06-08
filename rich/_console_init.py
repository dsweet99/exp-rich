"""Console constructor helpers."""
from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Optional, Tuple
from .color import ColorSystem
JUPYTER_DEFAULT_COLUMNS = 115
JUPYTER_DEFAULT_LINES = 100

def resolve_jupyter_size(environ: Mapping[str, str], width: Optional[int], height: Optional[int]) -> Tuple[Optional[int], Optional[int]]:
    if width is None:
        jupyter_columns = environ.get('JUPYTER_COLUMNS')
        if jupyter_columns is not None and jupyter_columns.isdigit():
            width = int(jupyter_columns)
        else:
            width = JUPYTER_DEFAULT_COLUMNS
    if height is None:
        jupyter_lines = environ.get('JUPYTER_LINES')
        if jupyter_lines is not None and jupyter_lines.isdigit():
            height = int(jupyter_lines)
        else:
            height = JUPYTER_DEFAULT_LINES
    return (width, height)

def resolve_terminal_size(environ: Mapping[str, str], legacy_windows: bool, width: Optional[int], height: Optional[int]) -> Tuple[Optional[int], Optional[int]]:
    if width is None:
        columns = environ.get('COLUMNS')
        if columns is not None and columns.isdigit():
            width = int(columns) - legacy_windows
    if height is None:
        lines = environ.get('LINES')
        if lines is not None and lines.isdigit():
            height = int(lines)
    return (width, height)

def resolve_force_interactive(environ: Mapping[str, str], force_interactive: Optional[bool]) -> Optional[bool]:
    if force_interactive is not None:
        return force_interactive
    tty_interactive = environ.get('TTY_INTERACTIVE', None)
    if tty_interactive is None:
        return None
    if tty_interactive == '0':
        return False
    if tty_interactive == '1':
        return True
    return None
_COLOR_SYSTEMS = {'standard': ColorSystem.STANDARD, '256': ColorSystem.EIGHT_BIT, 'truecolor': ColorSystem.TRUECOLOR, 'windows': ColorSystem.WINDOWS}

def resolve_color_system(console: 'Console', color_system: Optional[str]) -> Optional[ColorSystem]:
    if color_system is None:
        return None
    if color_system == 'auto':
        return console._detect_color_system()
    return _COLOR_SYSTEMS[color_system]
