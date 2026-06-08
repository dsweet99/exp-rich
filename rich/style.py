from __future__ import annotations

from functools import lru_cache
from itertools import count
from operator import attrgetter
from pickle import dumps, loads
from random import getrandbits
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Type, Union, cast, TYPE_CHECKING

from ._pick import M_COLOR, M_TERMINAL_THEME, rich_module
from .errors import StyleSyntaxError
from .repr import Result, rich_repr

if TYPE_CHECKING:
    from ._types import Color, ColorSystem, TerminalTheme



def _Color():
    return rich_module(M_COLOR).Color


def _ColorParseError():
    return rich_module(M_COLOR).ColorParseError


def _ColorSystem():
    return rich_module(M_COLOR).ColorSystem


def _blend_rgb():
    return rich_module(M_COLOR).blend_rgb

_hash_getter = attrgetter(
    "_color", "_bgcolor", "_attributes", "_set_attributes", "_link", "_meta"
)

# Style instances and style definitions are often interchangeable
StyleType = Union[str, "Style"]


_id_generator = count(getrandbits(24))


def _bit_init(self, bit_no: int) -> None:
    self.bit = 1 << bit_no


def _bit_get(self, obj: "Style", objtype: Type["Style"]) -> Optional[bool]:
    if obj._set_attributes & self.bit:
        return obj._attributes & self.bit != 0
    return None


_Bit = type(
    "_Bit",
    (),
    {
        "__doc__": "A descriptor to get/set a style attribute bit.",
        "__slots__": ["bit"],
        "__init__": _bit_init,
        "__get__": _bit_get,
    },
)


def _style_append_attribute_codes(
    sgr: List[str],
    attributes: int,
    style_map: Sequence[str],
) -> None:
    """Append ANSI SGR codes for style attributes."""
    append = sgr.append
    if attributes & 1:
        append(style_map[0])
    if attributes & 2:
        append(style_map[1])
    if attributes & 4:
        append(style_map[2])
    if attributes & 8:
        append(style_map[3])
    if attributes & 0b0000111110000:
        for bit in range(4, 9):
            if attributes & (1 << bit):
                append(style_map[bit])
    if attributes & 0b1111000000000:
        for bit in range(9, 13):
            if attributes & (1 << bit):
                append(style_map[bit])


def _style_append_toggle(
    append: Callable[[str], None],
    bits: int,
    bit: int,
    enabled: Optional[bool],
    true_name: str,
    false_name: str,
) -> None:
    if bits & bit:
        append(true_name if enabled else false_name)


def _style_append_text_attributes(
    append: Callable[[str], None], bits: int, style: "Style"
) -> None:
    if bits & 0b0000000001111:
        _style_append_toggle(append, bits, 1, style.bold, "bold", "not bold")
        _style_append_toggle(append, bits, 1 << 1, style.dim, "dim", "not dim")
        _style_append_toggle(
            append, bits, 1 << 2, style.italic, "italic", "not italic"
        )
        _style_append_toggle(
            append, bits, 1 << 3, style.underline, "underline", "not underline"
        )


def _style_append_display_attributes(
    append: Callable[[str], None], bits: int, style: "Style"
) -> None:
    if bits & 0b0000111110000:
        _style_append_toggle(append, bits, 1 << 4, style.blink, "blink", "not blink")
        _style_append_toggle(
            append, bits, 1 << 5, style.blink2, "blink2", "not blink2"
        )
        _style_append_toggle(
            append, bits, 1 << 6, style.reverse, "reverse", "not reverse"
        )
        _style_append_toggle(
            append, bits, 1 << 7, style.conceal, "conceal", "not conceal"
        )
        _style_append_toggle(
            append, bits, 1 << 8, style.strike, "strike", "not strike"
        )


def _style_append_extended_attributes(
    append: Callable[[str], None], bits: int, style: "Style"
) -> None:
    if bits & 0b1111000000000:
        _style_append_toggle(
            append, bits, 1 << 9, style.underline2, "underline2", "not underline2"
        )
        _style_append_toggle(append, bits, 1 << 10, style.frame, "frame", "not frame")
        _style_append_toggle(
            append, bits, 1 << 11, style.encircle, "encircle", "not encircle"
        )
        _style_append_toggle(
            append, bits, 1 << 12, style.overline, "overline", "not overline"
        )


def _style_build_definition(style: "Style") -> str:
    """Build a style definition string from style attributes."""
    attributes: List[str] = []
    append = attributes.append
    bits = style._set_attributes
    _style_append_text_attributes(append, bits, style)
    _style_append_display_attributes(append, bits, style)
    _style_append_extended_attributes(append, bits, style)
    if style._color is not None:
        append(style._color.name)
    if style._bgcolor is not None:
        append("on")
        append(style._bgcolor.name)
    if style._link:
        append("link")
        append(style._link)
    return " ".join(attributes) or "none"


def _style_html_color_rules(
    style: "Style",
    theme: TerminalTheme,
    append: Callable[[str], None],
) -> None:
    """Append CSS color rules for a style."""
    color = style.color
    bgcolor = style.bgcolor
    if style.reverse:
        color, bgcolor = bgcolor, color
    if style.dim:
        foreground_color = (
            theme.foreground_color if color is None else color.get_truecolor(theme)
        )
        color = _Color().from_triplet(
            _blend_rgb()(foreground_color, theme.background_color, 0.5)
        )
    if color is not None:
        theme_color = color.get_truecolor(theme)
        append(f"color: {theme_color.hex}")
        append(f"text-decoration-color: {theme_color.hex}")
    if bgcolor is not None:
        theme_color = bgcolor.get_truecolor(theme, foreground=False)
        append(f"background-color: {theme_color.hex}")


_USE_DEFAULT_COLOR_SYSTEM = object()


@rich_repr
class Style:
    """A terminal style.

    A terminal style consists of a color (`color`), a background color (`bgcolor`), and a number of attributes, such
    as bold, italic etc. The attributes have 3 states: they can either be on
    (``True``), off (``False``), or not set (``None``).

    Args:
        color (Union[Color, str], optional): Color of terminal text. Defaults to None.
        bgcolor (Union[Color, str], optional): Color of terminal background. Defaults to None.
        bold (bool, optional): Enable bold text. Defaults to None.
        dim (bool, optional): Enable dim text. Defaults to None.
        italic (bool, optional): Enable italic text. Defaults to None.
        underline (bool, optional): Enable underlined text. Defaults to None.
        blink (bool, optional): Enabled blinking text. Defaults to None.
        blink2 (bool, optional): Enable fast blinking text. Defaults to None.
        reverse (bool, optional): Enabled reverse text. Defaults to None.
        conceal (bool, optional): Enable concealed text. Defaults to None.
        strike (bool, optional): Enable strikethrough text. Defaults to None.
        underline2 (bool, optional): Enable doubly underlined text. Defaults to None.
        frame (bool, optional): Enable framed text. Defaults to None.
        encircle (bool, optional): Enable encircled text. Defaults to None.
        overline (bool, optional): Enable overlined text. Defaults to None.
        link (str, link): Link URL. Defaults to None.

    """

    _color: Optional[Color]
    _bgcolor: Optional[Color]
    _attributes: int
    _set_attributes: int
    _hash: Optional[int]
    _null: bool
    _meta: Optional[bytes]

    __slots__ = [
        "_color",
        "_bgcolor",
        "_attributes",
        "_set_attributes",
        "_link",
        "_link_id",
        "_ansi",
        "_style_definition",
        "_hash",
        "_null",
        "_meta",
    ]

    # maps bits on to SGR parameter
    _style_map = {
        0: "1",
        1: "2",
        2: "3",
        3: "4",
        4: "5",
        5: "6",
        6: "7",
        7: "8",
        8: "9",
        9: "21",
        10: "51",
        11: "52",
        12: "53",
    }

    STYLE_ATTRIBUTES = {
        "dim": "dim",
        "d": "dim",
        "bold": "bold",
        "b": "bold",
        "italic": "italic",
        "i": "italic",
        "underline": "underline",
        "u": "underline",
        "blink": "blink",
        "blink2": "blink2",
        "reverse": "reverse",
        "r": "reverse",
        "conceal": "conceal",
        "c": "conceal",
        "strike": "strike",
        "s": "strike",
        "underline2": "underline2",
        "uu": "underline2",
        "frame": "frame",
        "encircle": "encircle",
        "overline": "overline",
        "o": "overline",
    }

    def __init__(
        self,
        *,
        color: Optional[Union[Color, str]] = None,
        bgcolor: Optional[Union[Color, str]] = None,
        bold: Optional[bool] = None,
        dim: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None,
        blink: Optional[bool] = None,
        blink2: Optional[bool] = None,
        reverse: Optional[bool] = None,
        conceal: Optional[bool] = None,
        strike: Optional[bool] = None,
        underline2: Optional[bool] = None,
        frame: Optional[bool] = None,
        encircle: Optional[bool] = None,
        overline: Optional[bool] = None,
        link: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ):
        self._ansi: Optional[str] = None
        self._style_definition: Optional[str] = None

        def _make_color(color: Union[Color, str]) -> Color:
            Color = _Color()
            return color if isinstance(color, Color) else Color.parse(color)

        self._color = None if color is None else _make_color(color)
        self._bgcolor = None if bgcolor is None else _make_color(bgcolor)
        self._set_attributes = sum(
            (
                bold is not None,
                dim is not None and 2,
                italic is not None and 4,
                underline is not None and 8,
                blink is not None and 16,
                blink2 is not None and 32,
                reverse is not None and 64,
                conceal is not None and 128,
                strike is not None and 256,
                underline2 is not None and 512,
                frame is not None and 1024,
                encircle is not None and 2048,
                overline is not None and 4096,
            )
        )
        self._attributes = (
            sum(
                (
                    bold and 1 or 0,
                    dim and 2 or 0,
                    italic and 4 or 0,
                    underline and 8 or 0,
                    blink and 16 or 0,
                    blink2 and 32 or 0,
                    reverse and 64 or 0,
                    conceal and 128 or 0,
                    strike and 256 or 0,
                    underline2 and 512 or 0,
                    frame and 1024 or 0,
                    encircle and 2048 or 0,
                    overline and 4096 or 0,
                )
            )
            if self._set_attributes
            else 0
        )

        self._link = link
        self._meta = None if meta is None else dumps(meta)
        self._link_id = (
            f"{next(_id_generator)}{hash(self._meta)}" if (link or meta) else ""
        )
        self._hash: Optional[int] = None
        self._null = not (self._set_attributes or color or bgcolor or link or meta)

    @classmethod
    def null(cls) -> "Style":
        """Create an 'null' style, equivalent to Style(), but more performant."""
        return NULL_STYLE

    @classmethod
    def from_color(
        cls, color: Optional[Color] = None, bgcolor: Optional[Color] = None
    ) -> "Style":
        """Create a new style with colors and no attributes.

        Returns:
            color (Optional[Color]): A (foreground) color, or None for no color. Defaults to None.
            bgcolor (Optional[Color]): A (background) color, or None for no color. Defaults to None.
        """
        style: Style = cls.__new__(Style)
        style._ansi = None
        style._style_definition = None
        style._color = color
        style._bgcolor = bgcolor
        style._set_attributes = 0
        style._attributes = 0
        style._link = None
        style._link_id = ""
        style._meta = None
        style._null = not (color or bgcolor)
        style._hash = None
        return style

    @classmethod
    def from_meta(cls, meta: Optional[Dict[str, Any]]) -> "Style":
        """Create a new style with meta data.

        Returns:
            meta (Optional[Dict[str, Any]]): A dictionary of meta data. Defaults to None.
        """
        style: Style = cls.__new__(Style)
        style._ansi = None
        style._style_definition = None
        style._color = None
        style._bgcolor = None
        style._set_attributes = 0
        style._attributes = 0
        style._link = None
        style._meta = dumps(meta)
        style._link_id = f"{next(_id_generator)}{hash(style._meta)}"
        style._hash = None
        style._null = not (meta)
        return style

    @classmethod
    def on(cls, meta: Optional[Dict[str, Any]] = None, **handlers: Any) -> "Style":
        """Create a blank style with meta information.

        Example:
            style = Style.on(click=self.on_click)

        Args:
            meta (Optional[Dict[str, Any]], optional): An optional dict of meta information.
            **handlers (Any): Keyword arguments are translated in to handlers.

        Returns:
            Style: A Style with meta information attached.
        """
        meta = {} if meta is None else meta
        meta.update({f"@{key}": value for key, value in handlers.items()})
        return cls.from_meta(meta)

    bold = _Bit(0)
    dim = _Bit(1)
    italic = _Bit(2)
    underline = _Bit(3)
    blink = _Bit(4)
    blink2 = _Bit(5)
    reverse = _Bit(6)
    conceal = _Bit(7)
    strike = _Bit(8)
    underline2 = _Bit(9)
    frame = _Bit(10)
    encircle = _Bit(11)
    overline = _Bit(12)

    @property
    def link_id(self) -> str:
        """Get a link id, used in ansi code for links."""
        return self._link_id

    def __str__(self) -> str:
        """Re-generate style definition from attributes."""
        if self._style_definition is None:
            self._style_definition = _style_build_definition(self)
        return self._style_definition

    def __bool__(self) -> bool:
        """A Style is false if it has no attributes, colors, or links."""
        return not self._null

    def _make_ansi_codes(self, color_system: ColorSystem) -> str:
        """Generate ANSI codes for this style.

        Args:
            color_system (ColorSystem): Color system.

        Returns:
            str: String containing codes.
        """

        if self._ansi is None:
            sgr: List[str] = []
            attributes = self._attributes & self._set_attributes
            if attributes:
                _style_append_attribute_codes(sgr, attributes, self._style_map)
            if self._color is not None:
                sgr.extend(self._color.downgrade(color_system).get_ansi_codes())
            if self._bgcolor is not None:
                sgr.extend(
                    self._bgcolor.downgrade(color_system).get_ansi_codes(
                        foreground=False
                    )
                )
            self._ansi = ";".join(sgr)
        return self._ansi

    @classmethod
    @lru_cache(maxsize=1024)
    def normalize(cls, style: str) -> str:
        """Normalize a style definition so that styles with the same effect have the same string
        representation.

        Args:
            style (str): A style definition.

        Returns:
            str: Normal form of style definition.
        """
        try:
            return str(cls.parse(style))
        except StyleSyntaxError:
            return style.strip().lower()

    @classmethod
    def pick_first(cls, *values: Optional[StyleType]) -> StyleType:
        """Pick first non-None style."""
        for value in values:
            if value is not None:
                return value
        raise ValueError("expected at least one non-None style")

    def __rich_repr__(self) -> Result:
        yield "color", self.color, None
        yield "bgcolor", self.bgcolor, None
        yield "bold", self.bold, None,
        yield "dim", self.dim, None,
        yield "italic", self.italic, None
        yield "underline", self.underline, None,
        yield "blink", self.blink, None
        yield "blink2", self.blink2, None
        yield "reverse", self.reverse, None
        yield "conceal", self.conceal, None
        yield "strike", self.strike, None
        yield "underline2", self.underline2, None
        yield "frame", self.frame, None
        yield "encircle", self.encircle, None
        yield "link", self.link, None
        if self._meta:
            yield "meta", self.meta

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Style):
            return NotImplemented
        return self.__hash__() == other.__hash__()

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, Style):
            return NotImplemented
        return self.__hash__() != other.__hash__()

    def __hash__(self) -> int:
        if self._hash is not None:
            return self._hash
        self._hash = hash(_hash_getter(self))
        return self._hash

    @property
    def color(self) -> Optional[Color]:
        """The foreground color or None if it is not set."""
        return self._color

    @property
    def bgcolor(self) -> Optional[Color]:
        """The background color or None if it is not set."""
        return self._bgcolor

    @property
    def link(self) -> Optional[str]:
        """Link text, if set."""
        return self._link

    @property
    def transparent_background(self) -> bool:
        """Check if the style specified a transparent background."""
        return self.bgcolor is None or self.bgcolor.is_default

    @property
    def background_style(self) -> "Style":
        """A Style with background only."""
        return Style(bgcolor=self.bgcolor)

    @property
    def meta(self) -> Dict[str, Any]:
        """Get meta information (can not be changed after construction)."""
        return {} if self._meta is None else cast(Dict[str, Any], loads(self._meta))

    @property
    def without_color(self) -> "Style":
        """Get a copy of the style with color removed."""
        if self._null:
            return NULL_STYLE
        style: Style = self.__new__(Style)
        style._ansi = None
        style._style_definition = None
        style._color = None
        style._bgcolor = None
        style._attributes = self._attributes
        style._set_attributes = self._set_attributes
        style._link = self._link
        style._link_id = f"{next(_id_generator)}" if self._link else ""
        style._null = False
        style._meta = None
        style._hash = None
        return style

    @classmethod
    def _parse_color_token(cls, word: str, *, background: bool) -> str:
        ColorParseError = _ColorParseError()
        try:
            _Color().parse(word)
        except ColorParseError as error:
            label = "background color" if background else "color"
            raise StyleSyntaxError(
                f"unable to parse {word!r} as {label}; {error}"
            ) from None
        return word

    @classmethod
    def _parse_word(
        cls,
        original_word: str,
        words: Iterable[str],
        color: Optional[str],
        bgcolor: Optional[str],
        attributes: Dict[str, Optional[Any]],
        link: Optional[str],
    ) -> tuple[Optional[str], Optional[str], Dict[str, Optional[Any]], Optional[str]]:
        """Parse a single token from a style definition."""
        word = original_word.lower()
        if word == "on":
            next_word = next(words, "")
            if not next_word:
                raise StyleSyntaxError("color expected after 'on'")
            return color, cls._parse_color_token(next_word, background=True), attributes, link
        if word == "not":
            next_word = next(words, "")
            attribute = cls.STYLE_ATTRIBUTES.get(next_word)
            if attribute is None:
                raise StyleSyntaxError(
                    f"expected style attribute after 'not', found {next_word!r}"
                )
            attributes[attribute] = False
            return color, bgcolor, attributes, link
        if word == "link":
            next_word = next(words, "")
            if not next_word:
                raise StyleSyntaxError("URL expected after 'link'")
            return color, bgcolor, attributes, next_word
        if word in cls.STYLE_ATTRIBUTES:
            attributes[cls.STYLE_ATTRIBUTES[word]] = True
            return color, bgcolor, attributes, link
        return cls._parse_color_token(word, background=False), bgcolor, attributes, link

    @classmethod
    @lru_cache(maxsize=4096)
    def parse(cls, style_definition: str) -> "Style":
        """Parse a style definition.

        Args:
            style_definition (str): A string containing a style.

        Raises:
            StyleSyntaxError: If the style definition syntax is invalid.

        Returns:
            `Style`: A Style instance.
        """
        if style_definition.strip() == "none" or not style_definition:
            return cls.null()

        color: Optional[str] = None
        bgcolor: Optional[str] = None
        attributes: Dict[str, Optional[Any]] = {}
        link: Optional[str] = None

        words = iter(style_definition.split())
        for original_word in words:
            color, bgcolor, attributes, link = cls._parse_word(
                original_word, words, color, bgcolor, attributes, link
            )
        return Style(color=color, bgcolor=bgcolor, link=link, **attributes)

    @lru_cache(maxsize=1024)
    def get_html_style(self, theme: Optional[TerminalTheme] = None) -> str:
        """Get a CSS style rule."""
        theme = theme or rich_module(M_TERMINAL_THEME).DEFAULT_TERMINAL_THEME
        css: List[str] = []
        append = css.append
        _style_html_color_rules(self, theme, append)
        if self.bold:
            append("font-weight: bold")
        if self.italic:
            append("font-style: italic")
        if self.underline:
            append("text-decoration: underline")
        if self.strike:
            append("text-decoration: line-through")
        if self.overline:
            append("text-decoration: overline")
        return "; ".join(css)

    @classmethod
    def combine(cls, styles: Iterable["Style"]) -> "Style":
        """Combine styles and get result.

        Args:
            styles (Iterable[Style]): Styles to combine.

        Returns:
            Style: A new style instance.
        """
        iter_styles = iter(styles)
        return sum(iter_styles, next(iter_styles))

    @classmethod
    def chain(cls, *styles: "Style") -> "Style":
        """Combine styles from positional argument in to a single style.

        Args:
            *styles (Iterable[Style]): Styles to combine.

        Returns:
            Style: A new style instance.
        """
        iter_styles = iter(styles)
        return sum(iter_styles, next(iter_styles))

    def copy(self) -> "Style":
        """Get a copy of this style.

        Returns:
            Style: A new Style instance with identical attributes.
        """
        if self._null:
            return NULL_STYLE
        style: Style = self.__new__(Style)
        style._ansi = self._ansi
        style._style_definition = self._style_definition
        style._color = self._color
        style._bgcolor = self._bgcolor
        style._attributes = self._attributes
        style._set_attributes = self._set_attributes
        style._link = self._link
        style._link_id = f"{next(_id_generator)}" if self._link else ""
        style._hash = self._hash
        style._null = False
        style._meta = self._meta
        return style

    @lru_cache(maxsize=128)
    def clear_meta_and_links(self) -> "Style":
        """Get a copy of this style with link and meta information removed.

        Returns:
            Style: New style object.
        """
        if self._null:
            return NULL_STYLE
        style: Style = self.__new__(Style)
        style._ansi = self._ansi
        style._style_definition = self._style_definition
        style._color = self._color
        style._bgcolor = self._bgcolor
        style._attributes = self._attributes
        style._set_attributes = self._set_attributes
        style._link = None
        style._link_id = ""
        style._hash = None
        style._null = False
        style._meta = None
        return style

    def update_link(self, link: Optional[str] = None) -> "Style":
        """Get a copy with a different value for link.

        Args:
            link (str, optional): New value for link. Defaults to None.

        Returns:
            Style: A new Style instance.
        """
        style: Style = self.__new__(Style)
        style._ansi = self._ansi
        style._style_definition = self._style_definition
        style._color = self._color
        style._bgcolor = self._bgcolor
        style._attributes = self._attributes
        style._set_attributes = self._set_attributes
        style._link = link
        style._link_id = f"{next(_id_generator)}" if link else ""
        style._hash = None
        style._null = False
        style._meta = self._meta
        return style

    def render(
        self,
        text: str = "",
        *,
        color_system: object = _USE_DEFAULT_COLOR_SYSTEM,
        legacy_windows: bool = False,
    ) -> str:
        """Render the ANSI codes for the style.

        Args:
            text (str, optional): A string to style. Defaults to "".
            color_system (Optional[ColorSystem], optional): Color system to render to. Defaults to ColorSystem.TRUECOLOR.

        Returns:
            str: A string containing ANSI style codes.
        """
        if not text:
            return text
        if color_system is None:
            return text
        if color_system is _USE_DEFAULT_COLOR_SYSTEM:
            color_system = _ColorSystem().TRUECOLOR
        attrs = self._ansi or self._make_ansi_codes(color_system)
        rendered = f"\x1b[{attrs}m{text}\x1b[0m" if attrs else text
        if self._link and not legacy_windows:
            rendered = (
                f"\x1b]8;id={self._link_id};{self._link}\x1b\\{rendered}\x1b]8;;\x1b\\"
            )
        return rendered

    def test(self, text: Optional[str] = None) -> None:
        """Write text with style directly to terminal.

        This method is for testing purposes only.

        Args:
            text (Optional[str], optional): Text to style or None for style name.

        """
        import sys

        text = text or str(self)
        sys.stdout.write(f"{self.render(text)}\n")

    @lru_cache(maxsize=1024)
    def _add(self, style: Optional["Style"]) -> "Style":
        if style is None or style._null:
            return self
        if self._null:
            return style
        new_style: Style = self.__new__(Style)
        new_style._ansi = None
        new_style._style_definition = None
        new_style._color = style._color or self._color
        new_style._bgcolor = style._bgcolor or self._bgcolor
        new_style._attributes = (self._attributes & ~style._set_attributes) | (
            style._attributes & style._set_attributes
        )
        new_style._set_attributes = self._set_attributes | style._set_attributes
        new_style._link = style._link or self._link
        new_style._link_id = style._link_id or self._link_id
        new_style._null = style._null
        if self._meta and style._meta:
            new_style._meta = dumps({**self.meta, **style.meta})
        else:
            new_style._meta = self._meta or style._meta
        new_style._hash = None
        return new_style

    def __add__(self, style: Optional["Style"]) -> "Style":
        combined_style = self._add(style)
        return combined_style.copy() if combined_style.link else combined_style


NULL_STYLE = Style()


def _style_stack_init(self, default_style: "Style") -> None:
    self._stack: List[Style] = [default_style]


def _style_stack_repr(self) -> str:
    return f"<stylestack {self._stack!r}>"


def _style_stack_current(self) -> Style:
    return self._stack[-1]


def _style_stack_push(self, style: Style) -> None:
    self._stack.append(self._stack[-1] + style)


def _style_stack_pop(self) -> Style:
    self._stack.pop()
    return self._stack[-1]


StyleStack = type(
    "StyleStack",
    (),
    {
        "__doc__": "A stack of styles.",
        "__slots__": ["_stack"],
        "__init__": _style_stack_init,
        "__repr__": _style_stack_repr,
        "current": property(_style_stack_current),
        "push": _style_stack_push,
        "pop": _style_stack_pop,
    },
)
