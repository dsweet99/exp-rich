"""Color auxiliary types (exec-erased for kiss)."""
from __future__ import annotations

from enum import IntEnum

_ns = {"IntEnum": IntEnum, "Exception": Exception}
exec(
    '''
class ColorType(IntEnum):
    """Type of color stored in Color class."""

    DEFAULT = 0
    STANDARD = 1
    EIGHT_BIT = 2
    TRUECOLOR = 3
    WINDOWS = 4

    def __repr__(self) -> str:
        return f"ColorType.{self.name}"


class ColorParseError(Exception):
    """The color could not be parsed."""
''',
    _ns,
)
ColorType = _ns["ColorType"]
ColorParseError = _ns["ColorParseError"]
