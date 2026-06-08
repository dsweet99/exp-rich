import re
import sys
from colorsys import rgb_to_hls
from enum import IntEnum
from functools import lru_cache
from itertools import count
from operator import attrgetter
from pickle import dumps, loads
from random import getrandbits
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
)

from . import errors
from .color_triplet import ColorTriplet
from .repr import Result, rich_repr

if TYPE_CHECKING:  # pragma: no cover
    from .terminal_theme import TerminalTheme


WINDOWS = sys.platform == "win32"


@lru_cache(maxsize=1)
def _palettes():
    from .palette import EIGHT_BIT_PALETTE, STANDARD_PALETTE, WINDOWS_PALETTE

    return EIGHT_BIT_PALETTE, STANDARD_PALETTE, WINDOWS_PALETTE


class ColorSystem(IntEnum):
    """One of the 3 color system supported by terminals."""

    STANDARD = 1
    EIGHT_BIT = 2
    TRUECOLOR = 3
    WINDOWS = 4

    def __repr__(self) -> str:
        return f"ColorSystem.{self.name}"

    def __str__(self) -> str:
        return repr(self)


class ColorType(IntEnum):
    """Type of color stored in Color class."""

    DEFAULT = 0
    STANDARD = 1
    EIGHT_BIT = 2
    TRUECOLOR = 3
    WINDOWS = 4

    def __repr__(self) -> str:
        return f"ColorType.{self.name}"


ANSI_COLOR_NAMES = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
    "bright_black": 8,
    "bright_red": 9,
    "bright_green": 10,
    "bright_yellow": 11,
    "bright_blue": 12,
    "bright_magenta": 13,
    "bright_cyan": 14,
    "bright_white": 15,
    "grey0": 16,
    "gray0": 16,
    "navy_blue": 17,
    "dark_blue": 18,
    "blue3": 20,
    "blue1": 21,
    "dark_green": 22,
    "deep_sky_blue4": 25,
    "dodger_blue3": 26,
    "dodger_blue2": 27,
    "green4": 28,
    "spring_green4": 29,
    "turquoise4": 30,
    "deep_sky_blue3": 32,
    "dodger_blue1": 33,
    "green3": 40,
    "spring_green3": 41,
    "dark_cyan": 36,
    "light_sea_green": 37,
    "deep_sky_blue2": 38,
    "deep_sky_blue1": 39,
    "spring_green2": 47,
    "cyan3": 43,
    "dark_turquoise": 44,
    "turquoise2": 45,
    "green1": 46,
    "spring_green1": 48,
    "medium_spring_green": 49,
    "cyan2": 50,
    "cyan1": 51,
    "dark_red": 88,
    "deep_pink4": 125,
    "purple4": 55,
    "purple3": 56,
    "blue_violet": 57,
    "orange4": 94,
    "grey37": 59,
    "gray37": 59,
    "medium_purple4": 60,
    "slate_blue3": 62,
    "royal_blue1": 63,
    "chartreuse4": 64,
    "dark_sea_green4": 71,
    "pale_turquoise4": 66,
    "steel_blue": 67,
    "steel_blue3": 68,
    "cornflower_blue": 69,
    "chartreuse3": 76,
    "cadet_blue": 73,
    "sky_blue3": 74,
    "steel_blue1": 81,
    "pale_green3": 114,
    "sea_green3": 78,
    "aquamarine3": 79,
    "medium_turquoise": 80,
    "chartreuse2": 112,
    "sea_green2": 83,
    "sea_green1": 85,
    "aquamarine1": 122,
    "dark_slate_gray2": 87,
    "dark_magenta": 91,
    "dark_violet": 128,
    "purple": 129,
    "light_pink4": 95,
    "plum4": 96,
    "medium_purple3": 98,
    "slate_blue1": 99,
    "yellow4": 106,
    "wheat4": 101,
    "grey53": 102,
    "gray53": 102,
    "light_slate_grey": 103,
    "light_slate_gray": 103,
    "medium_purple": 104,
    "light_slate_blue": 105,
    "dark_olive_green3": 149,
    "dark_sea_green": 108,
    "light_sky_blue3": 110,
    "sky_blue2": 111,
    "dark_sea_green3": 150,
    "dark_slate_gray3": 116,
    "sky_blue1": 117,
    "chartreuse1": 118,
    "light_green": 120,
    "pale_green1": 156,
    "dark_slate_gray1": 123,
    "red3": 160,
    "medium_violet_red": 126,
    "magenta3": 164,
    "dark_orange3": 166,
    "indian_red": 167,
    "hot_pink3": 168,
    "medium_orchid3": 133,
    "medium_orchid": 134,
    "medium_purple2": 140,
    "dark_goldenrod": 136,
    "light_salmon3": 173,
    "rosy_brown": 138,
    "grey63": 139,
    "gray63": 139,
    "medium_purple1": 141,
    "gold3": 178,
    "dark_khaki": 143,
    "navajo_white3": 144,
    "grey69": 145,
    "gray69": 145,
    "light_steel_blue3": 146,
    "light_steel_blue": 147,
    "yellow3": 184,
    "dark_sea_green2": 157,
    "light_cyan3": 152,
    "light_sky_blue1": 153,
    "green_yellow": 154,
    "dark_olive_green2": 155,
    "dark_sea_green1": 193,
    "pale_turquoise1": 159,
    "deep_pink3": 162,
    "magenta2": 200,
    "hot_pink2": 169,
    "orchid": 170,
    "medium_orchid1": 207,
    "orange3": 172,
    "light_pink3": 174,
    "pink3": 175,
    "plum3": 176,
    "violet": 177,
    "light_goldenrod3": 179,
    "tan": 180,
    "misty_rose3": 181,
    "thistle3": 182,
    "plum2": 183,
    "khaki3": 185,
    "light_goldenrod2": 222,
    "light_yellow3": 187,
    "grey84": 188,
    "gray84": 188,
    "light_steel_blue1": 189,
    "yellow2": 190,
    "dark_olive_green1": 192,
    "honeydew2": 194,
    "light_cyan1": 195,
    "red1": 196,
    "deep_pink2": 197,
    "deep_pink1": 199,
    "magenta1": 201,
    "orange_red1": 202,
    "indian_red1": 204,
    "hot_pink": 206,
    "dark_orange": 208,
    "salmon1": 209,
    "light_coral": 210,
    "pale_violet_red1": 211,
    "orchid2": 212,
    "orchid1": 213,
    "orange1": 214,
    "sandy_brown": 215,
    "light_salmon1": 216,
    "light_pink1": 217,
    "pink1": 218,
    "plum1": 219,
    "gold1": 220,
    "navajo_white1": 223,
    "misty_rose1": 224,
    "thistle1": 225,
    "yellow1": 226,
    "light_goldenrod1": 227,
    "khaki1": 228,
    "wheat1": 229,
    "cornsilk1": 230,
    "grey100": 231,
    "gray100": 231,
    "grey3": 232,
    "gray3": 232,
    "grey7": 233,
    "gray7": 233,
    "grey11": 234,
    "gray11": 234,
    "grey15": 235,
    "gray15": 235,
    "grey19": 236,
    "gray19": 236,
    "grey23": 237,
    "gray23": 237,
    "grey27": 238,
    "gray27": 238,
    "grey30": 239,
    "gray30": 239,
    "grey35": 240,
    "gray35": 240,
    "grey39": 241,
    "gray39": 241,
    "grey42": 242,
    "gray42": 242,
    "grey46": 243,
    "gray46": 243,
    "grey50": 244,
    "gray50": 244,
    "grey54": 245,
    "gray54": 245,
    "grey58": 246,
    "gray58": 246,
    "grey62": 247,
    "gray62": 247,
    "grey66": 248,
    "gray66": 248,
    "grey70": 249,
    "gray70": 249,
    "grey74": 250,
    "gray74": 250,
    "grey78": 251,
    "gray78": 251,
    "grey82": 252,
    "gray82": 252,
    "grey85": 253,
    "gray85": 253,
    "grey89": 254,
    "gray89": 254,
    "grey93": 255,
    "gray93": 255,
}


class ColorParseError(Exception):
    """The color could not be parsed."""


def _parse_hex_color(cls: type["Color"], color: str, color_24: str) -> "Color":
    triplet = ColorTriplet(
        int(color_24[0:2], 16), int(color_24[2:4], 16), int(color_24[4:6], 16)
    )
    return cls(color, ColorType.TRUECOLOR, triplet=triplet)


def _parse_8bit_color(cls: type["Color"], color: str, color_8: str) -> "Color":
    number = int(color_8)
    if number > 255:
        raise ColorParseError(f"color number must be <= 255 in {color!r}")
    return cls(
        color,
        type=(ColorType.STANDARD if number < 16 else ColorType.EIGHT_BIT),
        number=number,
    )


def _parse_rgb_color(cls: type["Color"], color: str, color_rgb: str, original_color: str) -> "Color":
    components = color_rgb.split(",")
    if len(components) != 3:
        raise ColorParseError(f"expected three components in {original_color!r}")
    red, green, blue = components
    triplet = ColorTriplet(int(red), int(green), int(blue))
    if not all(component <= 255 for component in triplet):
        raise ColorParseError(
            f"color components must be <= 255 in {original_color!r}"
        )
    return cls(color, ColorType.TRUECOLOR, triplet=triplet)


def _downgrade_truecolor_eight_bit(color: "Color") -> "Color":
    assert color.triplet is not None
    _h, lightness, s = rgb_to_hls(*color.triplet.normalized)
    if s < 0.15:
        gray = round(lightness * 25.0)
        if gray == 0:
            color_number = 16
        elif gray == 25:
            color_number = 231
        else:
            color_number = 231 + gray
        return Color(color.name, ColorType.EIGHT_BIT, number=color_number)

    red, green, blue = color.triplet
    six_red = red / 95 if red < 95 else 1 + (red - 95) / 40
    six_green = green / 95 if green < 95 else 1 + (green - 95) / 40
    six_blue = blue / 95 if blue < 95 else 1 + (blue - 95) / 40
    color_number = 16 + 36 * round(six_red) + 6 * round(six_green) + round(six_blue)
    return Color(color.name, ColorType.EIGHT_BIT, number=color_number)


def _downgrade_to_standard(color: "Color") -> "Color":
    if color.system == ColorSystem.TRUECOLOR:
        assert color.triplet is not None
        triplet = color.triplet
    else:
        assert color.number is not None
        eight_bit, _, _ = _palettes()
        triplet = ColorTriplet(*eight_bit[color.number])
    _, standard, _ = _palettes()
    color_number = standard.match(triplet)
    return Color(color.name, ColorType.STANDARD, number=color_number)


def _downgrade_to_windows(color: "Color") -> "Color":
    if color.system == ColorSystem.TRUECOLOR:
        assert color.triplet is not None
        triplet = color.triplet
    else:
        assert color.number is not None
        if color.number < 16:
            return Color(color.name, ColorType.WINDOWS, number=color.number)
        eight_bit, _, _ = _palettes()
        triplet = ColorTriplet(*eight_bit[color.number])
    _, _, windows = _palettes()
    color_number = windows.match(triplet)
    return Color(color.name, ColorType.WINDOWS, number=color_number)


RE_COLOR = re.compile(
    r"""^
\#([0-9a-f]{6})$|
color\(([0-9]{1,3})\)$|
rgb\(([\d\s,]+)\)$
""",
    re.VERBOSE,
)


@rich_repr
class Color(NamedTuple):
    """Terminal color definition."""

    name: str
    """The name of the color (typically the input to Color.parse)."""
    type: ColorType
    """The type of the color."""
    number: Optional[int] = None
    """The color number, if a standard color, or None."""
    triplet: Optional[ColorTriplet] = None
    """A triplet of color components, if an RGB color."""

    def __rich__(self) -> str:
        """Displays the actual color if Rich printed."""
        return f"<color {self.name!r} ({self.type.name.lower()})>"

    def __rich_repr__(self) -> Result:
        yield self.name
        yield self.type
        yield "number", self.number, None
        yield "triplet", self.triplet, None

    @property
    def system(self) -> ColorSystem:
        """Get the native color system for this color."""
        if self.type == ColorType.DEFAULT:
            return ColorSystem.STANDARD
        return ColorSystem(int(self.type))

    @property
    def is_system_defined(self) -> bool:
        """Check if the color is ultimately defined by the system."""
        return self.system not in (ColorSystem.EIGHT_BIT, ColorSystem.TRUECOLOR)

    @property
    def is_default(self) -> bool:
        """Check if the color is a default color."""
        return self.type == ColorType.DEFAULT

    def get_truecolor(
        self, theme: Optional["TerminalTheme"] = None, foreground: bool = True
    ) -> ColorTriplet:
        """Get an equivalent color triplet for this color.

        Args:
            theme (TerminalTheme, optional): Optional terminal theme, or None to use default. Defaults to None.
            foreground (bool, optional): True for a foreground color, or False for background. Defaults to True.

        Returns:
            ColorTriplet: A color triplet containing RGB components.
        """

        if theme is None:
            from .terminal_theme import DEFAULT_TERMINAL_THEME

            theme = DEFAULT_TERMINAL_THEME
        if self.type == ColorType.TRUECOLOR:
            assert self.triplet is not None
            return self.triplet
        elif self.type == ColorType.EIGHT_BIT:
            assert self.number is not None
            eight_bit, _, _ = _palettes()
            return eight_bit[self.number]
        elif self.type == ColorType.STANDARD:
            assert self.number is not None
            return theme.ansi_colors[self.number]
        elif self.type == ColorType.WINDOWS:
            assert self.number is not None
            _, _, windows = _palettes()
            return windows[self.number]
        else:  # self.type == ColorType.DEFAULT:
            assert self.number is None
            return theme.foreground_color if foreground else theme.background_color

    @classmethod
    def from_ansi(cls, number: int) -> "Color":
        """Create a Color number from it's 8-bit ansi number.

        Args:
            number (int): A number between 0-255 inclusive.

        Returns:
            Color: A new Color instance.
        """
        return cls(
            name=f"color({number})",
            type=(ColorType.STANDARD if number < 16 else ColorType.EIGHT_BIT),
            number=number,
        )

    @classmethod
    def from_triplet(cls, triplet: "ColorTriplet") -> "Color":
        """Create a truecolor RGB color from a triplet of values.

        Args:
            triplet (ColorTriplet): A color triplet containing red, green and blue components.

        Returns:
            Color: A new color object.
        """
        return cls(name=triplet.hex, type=ColorType.TRUECOLOR, triplet=triplet)

    @classmethod
    def from_rgb(cls, red: float, green: float, blue: float) -> "Color":
        """Create a truecolor from three color components in the range(0->255).

        Args:
            red (float): Red component in range 0-255.
            green (float): Green component in range 0-255.
            blue (float): Blue component in range 0-255.

        Returns:
            Color: A new color object.
        """
        return cls.from_triplet(ColorTriplet(int(red), int(green), int(blue)))

    @classmethod
    def default(cls) -> "Color":
        """Get a Color instance representing the default color.

        Returns:
            Color: Default color.
        """
        return cls(name="default", type=ColorType.DEFAULT)

    @classmethod
    @lru_cache(maxsize=1024)
    def parse(cls, color: str) -> "Color":
        """Parse a color definition."""
        original_color = color
        color = color.lower().strip()

        if color == "default":
            return cls(color, type=ColorType.DEFAULT)

        color_number = ANSI_COLOR_NAMES.get(color)
        if color_number is not None:
            return cls(
                color,
                type=(ColorType.STANDARD if color_number < 16 else ColorType.EIGHT_BIT),
                number=color_number,
            )

        color_match = RE_COLOR.match(color)
        if color_match is None:
            raise ColorParseError(f"{original_color!r} is not a valid color")

        color_24, color_8, color_rgb = color_match.groups()
        if color_24:
            return _parse_hex_color(cls, color, color_24)
        if color_8:
            return _parse_8bit_color(cls, color, color_8)
        return _parse_rgb_color(cls, color, color_rgb, original_color)

    @lru_cache(maxsize=1024)
    def get_ansi_codes(self, foreground: bool = True) -> Tuple[str, ...]:
        """Get the ANSI escape codes for this color."""
        _type = self.type
        if _type == ColorType.DEFAULT:
            return ("39" if foreground else "49",)

        elif _type == ColorType.WINDOWS:
            number = self.number
            assert number is not None
            fore, back = (30, 40) if number < 8 else (82, 92)
            return (str(fore + number if foreground else back + number),)

        elif _type == ColorType.STANDARD:
            number = self.number
            assert number is not None
            fore, back = (30, 40) if number < 8 else (82, 92)
            return (str(fore + number if foreground else back + number),)

        elif _type == ColorType.EIGHT_BIT:
            assert self.number is not None
            return ("38" if foreground else "48", "5", str(self.number))

        else:  # self.standard == ColorStandard.TRUECOLOR:
            assert self.triplet is not None
            red, green, blue = self.triplet
            return ("38" if foreground else "48", "2", str(red), str(green), str(blue))

    @lru_cache(maxsize=1024)
    def downgrade(self, system: ColorSystem) -> "Color":
        """Downgrade a color system to a system with fewer colors."""

        if self.type in (ColorType.DEFAULT, system):
            return self
        # Convert to 8-bit color from truecolor color
        if system == ColorSystem.EIGHT_BIT and self.system == ColorSystem.TRUECOLOR:
            return _downgrade_truecolor_eight_bit(self)
        if system == ColorSystem.STANDARD:
            return _downgrade_to_standard(self)
        if system == ColorSystem.WINDOWS:
            return _downgrade_to_windows(self)
        return self


def parse_rgb_hex(hex_color: str) -> ColorTriplet:
    """Parse six hex characters in to RGB triplet."""
    assert len(hex_color) == 6, "must be 6 characters"
    color = ColorTriplet(
        int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    )
    return color


def blend_rgb(
    color1: ColorTriplet, color2: ColorTriplet, cross_fade: float = 0.5
) -> ColorTriplet:
    """Blend one RGB color in to another."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    new_color = ColorTriplet(
        int(r1 + (r2 - r1) * cross_fade),
        int(g1 + (g2 - g1) * cross_fade),
        int(b1 + (b2 - b1) * cross_fade),
    )
    return new_color


# --- Style (merged from style.py) ---

_hash_getter = attrgetter(
    "_color", "_bgcolor", "_attributes", "_set_attributes", "_link", "_meta"
)

# Style instances and style definitions are often interchangeable
StyleType = Union[str, "Style"]


_id_generator = count(getrandbits(24))


def _append_style_toggle_bits(
    bits: int, style: "Style", append, specs: List[Tuple[int, str, str, str]]
) -> None:
    for bit, attr_name, enabled_label, disabled_label in specs:
        if bits & bit:
            append(enabled_label if getattr(style, attr_name) else disabled_label)


def _style_definition_parts(style: "Style") -> List[str]:
    attributes: List[str] = []
    append = attributes.append
    bits = style._set_attributes
    _append_style_toggle_bits(
        bits,
        style,
        append,
        [
            (1, "bold", "bold", "not bold"),
            (2, "dim", "dim", "not dim"),
            (4, "italic", "italic", "not italic"),
            (8, "underline", "underline", "not underline"),
        ],
    )
    _append_style_toggle_bits(
        bits,
        style,
        append,
        [
            (1 << 4, "blink", "blink", "not blink"),
            (1 << 5, "blink2", "blink2", "not blink2"),
            (1 << 6, "reverse", "reverse", "not reverse"),
            (1 << 7, "conceal", "conceal", "not conceal"),
            (1 << 8, "strike", "strike", "not strike"),
        ],
    )
    _append_style_toggle_bits(
        bits,
        style,
        append,
        [
            (1 << 9, "underline2", "underline2", "not underline2"),
            (1 << 10, "frame", "frame", "not frame"),
            (1 << 11, "encircle", "encircle", "not encircle"),
            (1 << 12, "overline", "overline", "not overline"),
        ],
    )
    if style._color is not None:
        append(style._color.name)
    if style._bgcolor is not None:
        append("on")
        append(style._bgcolor.name)
    if style._link:
        append("link")
        append(style._link)
    return attributes


def _append_sgr_attribute_bits(attributes: int, style_map: List[str], append) -> None:
    if attributes & 1:
        append(style_map[0])
    if attributes & 2:
        append(style_map[1])
    if attributes & 4:
        append(style_map[2])
    if attributes & 8:
        append(style_map[3])
    for bit in range(4, 9):
        if attributes & (1 << bit):
            append(style_map[bit])
    for bit in range(9, 13):
        if attributes & (1 << bit):
            append(style_map[bit])


def _style_sgr_parts(style: "Style", color_system: ColorSystem) -> List[str]:
    sgr: List[str] = []
    attributes = style._attributes & style._set_attributes
    if attributes:
        _append_sgr_attribute_bits(attributes, style._style_map, sgr.append)
    if style._color is not None:
        sgr.extend(style._color.downgrade(color_system).get_ansi_codes())
    if style._bgcolor is not None:
        sgr.extend(
            style._bgcolor.downgrade(color_system).get_ansi_codes(foreground=False)
        )
    return sgr


def _parse_style_on_token(
    word: str, words: Iterable[str], color: Optional[str], link: Optional[str]
) -> Tuple[Optional[str], Optional[str], Optional[str], Iterable[str]]:
    word = next(words, "")
    if not word:
        raise errors.StyleSyntaxError("color expected after 'on'")
    try:
        Color.parse(word)
    except ColorParseError as error:
        raise errors.StyleSyntaxError(
            f"unable to parse {word!r} as background color; {error}"
        ) from None
    return color, word, link, words


def _parse_style_not_token(
    word: str,
    words: Iterable[str],
    *,
    attributes: Dict[str, Optional[Any]],
    color: Optional[str],
    bgcolor: Optional[str],
    link: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str], Iterable[str]]:
    STYLE_ATTRIBUTES = Style.STYLE_ATTRIBUTES
    word = next(words, "")
    attribute = STYLE_ATTRIBUTES.get(word)
    if attribute is None:
        raise errors.StyleSyntaxError(
            f"expected style attribute after 'not', found {word!r}"
        )
    attributes[attribute] = False
    return color, bgcolor, link, words


def _parse_style_token(
    word: str,
    words: Iterable[str],
    *,
    attributes: Dict[str, Optional[Any]],
    color: Optional[str],
    bgcolor: Optional[str],
    link: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str], Iterable[str]]:
    STYLE_ATTRIBUTES = Style.STYLE_ATTRIBUTES
    if word == "on":
        return _parse_style_on_token(word, words, color, link)
    if word == "not":
        return _parse_style_not_token(
            word, words, attributes=attributes, color=color, bgcolor=bgcolor, link=link
        )
    if word == "link":
        word = next(words, "")
        if not word:
            raise errors.StyleSyntaxError("URL expected after 'link'")
        return color, bgcolor, word, words
    if word in STYLE_ATTRIBUTES:
        attributes[STYLE_ATTRIBUTES[word]] = True
        return color, bgcolor, link, words
    try:
        Color.parse(word)
    except ColorParseError as error:
        raise errors.StyleSyntaxError(
            f"unable to parse {word!r} as color; {error}"
        ) from None
    return word, bgcolor, link, words


def _style_css_color_parts(style: "Style", theme: "TerminalTheme", append) -> None:
    color = style.color
    bgcolor = style.bgcolor
    if style.reverse:
        color, bgcolor = bgcolor, color
    if style.dim:
        foreground_color = (
            theme.foreground_color if color is None else color.get_truecolor(theme)
        )
        color = Color.from_triplet(
            blend_rgb(foreground_color, theme.background_color, 0.5)
        )
    if color is not None:
        theme_color = color.get_truecolor(theme)
        append(f"color: {theme_color.hex}")
        append(f"text-decoration-color: {theme_color.hex}")
    if bgcolor is not None:
        theme_color = bgcolor.get_truecolor(theme, foreground=False)
        append(f"background-color: {theme_color.hex}")


def _style_css_parts(style: "Style", theme: "TerminalTheme") -> List[str]:
    css: List[str] = []
    append = css.append
    _style_css_color_parts(style, theme, append)
    if style.bold:
        append("font-weight: bold")
    if style.italic:
        append("font-style: italic")
    if style.underline:
        append("text-decoration: underline")
    if style.strike:
        append("text-decoration: line-through")
    if style.overline:
        append("text-decoration: overline")
    return css


class _Bit:
    """A descriptor to get/set a style attribute bit."""

    __slots__ = ["bit"]

    def __init__(self, bit_no: int) -> None:
        self.bit = 1 << bit_no

    def __get__(self, obj: "Style", objtype: Type["Style"]) -> Optional[bool]:
        if obj._set_attributes & self.bit:
            return obj._attributes & self.bit != 0
        return None


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
            self._style_definition = " ".join(_style_definition_parts(self)) or "none"
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
            self._ansi = ";".join(_style_sgr_parts(self, color_system))
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
        except errors.StyleSyntaxError:
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
    @lru_cache(maxsize=4096)
    def parse(cls, style_definition: str) -> "Style":
        """Parse a style definition.

        Args:
            style_definition (str): A string containing a style.

        Raises:
            errors.StyleSyntaxError: If the style definition syntax is invalid.

        Returns:
            `Style`: A Style instance.
        """
        if style_definition.strip() == "none" or not style_definition:
            return cls.null()

        STYLE_ATTRIBUTES = cls.STYLE_ATTRIBUTES
        color: Optional[str] = None
        bgcolor: Optional[str] = None
        attributes: Dict[str, Optional[Any]] = {}
        link: Optional[str] = None

        words = iter(style_definition.split())
        for original_word in words:
            word = original_word.lower()
            color, bgcolor, link, _ = _parse_style_token(
                word,
                words,
                attributes=attributes,
                color=color,
                bgcolor=bgcolor,
                link=link,
            )
        style = Style(color=color, bgcolor=bgcolor, link=link, **attributes)
        return style

    @lru_cache(maxsize=1024)
    def get_html_style(self, theme: Optional["TerminalTheme"] = None) -> str:
        """Get a CSS style rule."""
        if theme is None:
            from .terminal_theme import DEFAULT_TERMINAL_THEME

            theme = DEFAULT_TERMINAL_THEME
        return "; ".join(_style_css_parts(self, theme))

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
        color_system: Optional[ColorSystem] = ColorSystem.TRUECOLOR,
        legacy_windows: bool = False,
    ) -> str:
        """Render the ANSI codes for the style.

        Args:
            text (str, optional): A string to style. Defaults to "".
            color_system (Optional[ColorSystem], optional): Color system to render to. Defaults to ColorSystem.TRUECOLOR.

        Returns:
            str: A string containing ANSI style codes.
        """
        if not text or color_system is None:
            return text
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


class StyleStack:
    """A stack of styles."""

    __slots__ = ["_stack"]

    def __init__(self, default_style: "Style") -> None:
        self._stack: List[Style] = [default_style]

    def __repr__(self) -> str:
        return f"<stylestack {self._stack!r}>"

    @property
    def current(self) -> Style:
        """Get the Style at the top of the stack."""
        return self._stack[-1]

    def push(self, style: Style) -> None:
        """Push a new style on to the stack.

        Args:
            style (Style): New style to combine with current style.
        """
        self._stack.append(self._stack[-1] + style)

    def pop(self) -> Style:
        """Pop last style and discard.

        Returns:
            Style: New current style (also available as stack.current)
        """
        self._stack.pop()
        return self._stack[-1]
