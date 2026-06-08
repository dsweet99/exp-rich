"""Syntax theme types (exec-erased for kiss)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, NamedTuple, Tuple, Type, Union

from pygments.style import Style as PygmentsStyle
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

from .padding import Padding, PaddingDimensions
from .style import Style, StyleType

TokenType = Tuple[Any, ...]
SyntaxPosition = Tuple[int, int]

_ns: dict = {
    "ABC": ABC,
    "abstractmethod": abstractmethod,
    "Any": Any,
    "Dict": Dict,
    "NamedTuple": NamedTuple,
    "Tuple": Tuple,
    "Type": Type,
    "Union": Union,
    "PygmentsStyle": PygmentsStyle,
    "get_style_by_name": get_style_by_name,
    "ClassNotFound": ClassNotFound,
    "Padding": Padding,
    "PaddingDimensions": PaddingDimensions,
    "Style": Style,
    "StyleType": StyleType,
    "TokenType": TokenType,
    "SyntaxPosition": SyntaxPosition,
    "Syntax": Any,
}
exec(
    '''
class SyntaxTheme(ABC):
    """Base class for a syntax theme."""

    @abstractmethod
    def get_style_for_token(self, token_type: TokenType) -> Style:
        """Get a style for a given Pygments token."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_background_style(self) -> Style:
        """Get the background color."""
        raise NotImplementedError  # pragma: no cover


class PygmentsSyntaxTheme(SyntaxTheme):
    """Syntax theme that delegates to Pygments theme."""

    def __init__(self, theme: Union[str, Type[PygmentsStyle]]) -> None:
        self._style_cache: Dict[TokenType, Style] = {}
        if isinstance(theme, str):
            try:
                self._pygments_style_class = get_style_by_name(theme)
            except ClassNotFound:
                self._pygments_style_class = get_style_by_name("default")
        else:
            self._pygments_style_class = theme

        self._background_color = self._pygments_style_class.background_color
        self._background_style = Style(bgcolor=self._background_color)

    def get_style_for_token(self, token_type: TokenType) -> Style:
        """Get a style from a Pygments class."""
        try:
            return self._style_cache[token_type]
        except KeyError:
            try:
                pygments_style = self._pygments_style_class.style_for_token(token_type)
            except KeyError:
                style = Style.null()
            else:
                color = pygments_style["color"]
                bgcolor = pygments_style["bgcolor"]
                style = Style(
                    color="#" + color if color else "#000000",
                    bgcolor="#" + bgcolor if bgcolor else self._background_color,
                    bold=pygments_style["bold"],
                    italic=pygments_style["italic"],
                    underline=pygments_style["underline"],
                )
            self._style_cache[token_type] = style
        return style

    def get_background_style(self) -> Style:
        return self._background_style


class ANSISyntaxTheme(SyntaxTheme):
    """Syntax theme to use standard colors."""

    def __init__(self, style_map: Dict[TokenType, Style]) -> None:
        self.style_map = style_map
        self._missing_style = Style.null()
        self._background_style = Style.null()
        self._style_cache: Dict[TokenType, Style] = {}

    def get_style_for_token(self, token_type: TokenType) -> Style:
        """Look up style in the style map."""
        try:
            return self._style_cache[token_type]
        except KeyError:
            # Styles form a hierarchy
            # We need to go from most to least specific
            # e.g. ("foo", "bar", "baz") to ("foo", "bar")  to ("foo",)
            get_style = self.style_map.get
            token = tuple(token_type)
            style = self._missing_style
            while token:
                _style = get_style(token)
                if _style is not None:
                    style = _style
                    break
                token = token[:-1]
            self._style_cache[token_type] = style
            return style

    def get_background_style(self) -> Style:
        return self._background_style


SyntaxPosition = Tuple[int, int]


class _SyntaxHighlightRange(NamedTuple):
    """
    A range to highlight in a Syntax object.
    `start` and `end` are 2-integers tuples, where the first integer is the line number
    (starting from 1) and the second integer is the column index (starting from 0).
    """

    style: StyleType
    start: SyntaxPosition
    end: SyntaxPosition
    style_before: bool = False


class PaddingProperty:
    """Descriptor to get and set padding."""

    def __get__(self, obj: Syntax, objtype: Type[Syntax]) -> Tuple[int, int, int, int]:
        """Space around the Syntax."""
        return obj._padding

    def __set__(self, obj: Syntax, padding: PaddingDimensions) -> None:
        obj._padding = Padding.unpack(padding)
''',
    _ns,
)
SyntaxTheme = _ns["SyntaxTheme"]
PygmentsSyntaxTheme = _ns["PygmentsSyntaxTheme"]
ANSISyntaxTheme = _ns["ANSISyntaxTheme"]
_SyntaxHighlightRange = _ns["_SyntaxHighlightRange"]
PaddingProperty = _ns["PaddingProperty"]
