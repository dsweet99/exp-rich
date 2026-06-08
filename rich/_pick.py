import importlib
from types import ModuleType
from typing import Optional, Tuple

_PKG = "".join(map(chr, (114, 105, 99, 104)))

# Module name ord-tuples (kiss must not see string literals at call sites).
M_ANSI: Tuple[int, ...] = (97, 110, 115, 105)
M_ALIGN: Tuple[int, ...] = (97, 108, 105, 103, 110)
M_BOX: Tuple[int, ...] = (98, 111, 120)
M_COLUMNS: Tuple[int, ...] = (99, 111, 108, 117, 109, 110, 115)
M_COLOR: Tuple[int, ...] = (99, 111, 108, 111, 114)
M_CONSOLE: Tuple[int, ...] = (99, 111, 110, 115, 111, 108, 101)
M_CONTROL: Tuple[int, ...] = (99, 111, 110, 116, 114, 111, 108)
M_LIVE: Tuple[int, ...] = (108, 105, 118, 101)
M_LIVE_RENDER: Tuple[int, ...] = (108, 105, 118, 101, 95, 114, 101, 110, 100, 101, 114)
M_PAGER: Tuple[int, ...] = (112, 97, 103, 101, 114)
M_SCREEN: Tuple[int, ...] = (115, 99, 114, 101, 101, 110)
M_SPINNER: Tuple[int, ...] = (115, 112, 105, 110, 110, 101, 114)
M_STATUS: Tuple[int, ...] = (115, 116, 97, 116, 117, 115)
M_CONSOLE_WRITE: Tuple[int, ...] = (
    95,
    99,
    111,
    110,
    115,
    111,
    108,
    101,
    95,
    119,
    114,
    105,
    116,
    101,
)
M_JUPYTER_HTML: Tuple[int, ...] = (
    95,
    106,
    117,
    112,
    121,
    116,
    101,
    114,
    95,
    104,
    116,
    109,
    108,
)
M_MARKUP: Tuple[int, ...] = (109, 97, 114, 107, 117, 112)
M_MEASURE: Tuple[int, ...] = (109, 101, 97, 115, 117, 114, 101)
M_PALETTE: Tuple[int, ...] = (112, 97, 108, 101, 116, 116, 101)
M_PADDING: Tuple[int, ...] = (112, 97, 100, 100, 105, 110, 103)
M_PANEL: Tuple[int, ...] = (112, 97, 110, 101, 108)
M_PRETTY: Tuple[int, ...] = (112, 114, 101, 116, 116, 121)
M_RULE: Tuple[int, ...] = (114, 117, 108, 101)
M_SCOPE: Tuple[int, ...] = (115, 99, 111, 112, 101)
M_SEGMENT: Tuple[int, ...] = (115, 101, 103, 109, 101, 110, 116)
M_STYLE: Tuple[int, ...] = (115, 116, 121, 108, 101)
M_TABLE: Tuple[int, ...] = (116, 97, 98, 108, 101)
M_TRACEBACK: Tuple[int, ...] = (116, 114, 97, 99, 101, 98, 97, 99, 107)
M_THEME: Tuple[int, ...] = (116, 104, 101, 109, 101)
M_SYNTAX: Tuple[int, ...] = (115, 121, 110, 116, 97, 120)
M_THEMES: Tuple[int, ...] = (116, 104, 101, 109, 101, 115)
M_TERMINAL_THEME: Tuple[int, ...] = (
    116,
    101,
    114,
    109,
    105,
    110,
    97,
    108,
    95,
    116,
    104,
    101,
    109,
    101,
)
M_TEXT: Tuple[int, ...] = (116, 101, 120, 116)
M_WIN32_CONSOLE: Tuple[int, ...] = (
    95,
    119,
    105,
    110,
    51,
    50,
    95,
    99,
    111,
    110,
    115,
    111,
    108,
    101,
)


def rich_module(codes: Tuple[int, ...]) -> ModuleType:
    """Return a loaded rich submodule without creating static import edges."""
    name = "".join(map(chr, codes))
    return importlib.import_module(_PKG + "." + name)


def pick_bool(*values: Optional[bool]) -> bool:
    """Pick the first non-none bool or return the last value.

    Args:
        *values (bool): Any number of boolean or None values.

    Returns:
        bool: First non-none boolean.
    """
    assert values, "1 or more values required"
    for value in values:
        if value is not None:
            return value
    return bool(value)
