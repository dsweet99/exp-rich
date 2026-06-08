from __future__ import annotations

import os.path
import re
import sys
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    Callable,
)

from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
from pygments.style import Style as PygmentsStyle
from pygments.styles import get_style_by_name
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Name,
    Number,
    Operator,
    String,
    Token,
    Whitespace,
)
from pygments.util import ClassNotFound

from ._lazy import Lazy
from ._lines import Lines
from ._loop import loop_first
from ._pick import M_COLOR, M_PADDING, M_SEGMENT, M_STYLE, M_TEXT, rich_module
from .cells import cell_len
from ._jupyter_mixin import JupyterMixin
from .measure import Measurement
from ._padding_dims import PaddingDimensions

StyleType = Union[str, "Style"]


def _Segment():
    return rich_module(M_SEGMENT).Segment


def _Segments():
    return rich_module(M_SEGMENT).Segments


def _Text():
    return rich_module(M_TEXT).Text


def _Style():
    return rich_module(M_STYLE).Style


def _Padding():
    return rich_module(M_PADDING).Padding


def _Color():
    return rich_module(M_COLOR).Color


def _blend_rgb():
    return rich_module(M_COLOR).blend_rgb


if TYPE_CHECKING:
    from ._types import ConsoleOptions, JustifyMethod, RenderResult


Segment = Lazy(_Segment)
Segments = Lazy(_Segments)
Text = Lazy(_Text)
Style = Lazy(_Style)
Padding = Lazy(_Padding)
Color = Lazy(_Color)
blend_rgb = Lazy(_blend_rgb)

TokenType = Tuple[str, ...]

WINDOWS = sys.platform == "win32"
DEFAULT_THEME = "monokai"

# The following styles are based on https://github.com/pygments/pygments/blob/master/pygments/formatters/terminal.py
# A few modifications were made

ANSI_LIGHT: Dict[TokenType, Style] = {
    Token: Style(),
    Whitespace: Style(color="white"),
    Comment: Style(dim=True),
    Comment.Preproc: Style(color="cyan"),
    Keyword: Style(color="blue"),
    Keyword.Type: Style(color="cyan"),
    Operator.Word: Style(color="magenta"),
    Name.Builtin: Style(color="cyan"),
    Name.Function: Style(color="green"),
    Name.Namespace: Style(color="cyan", underline=True),
    Name.Class: Style(color="green", underline=True),
    Name.Exception: Style(color="cyan"),
    Name.Decorator: Style(color="magenta", bold=True),
    Name.Variable: Style(color="red"),
    Name.Constant: Style(color="red"),
    Name.Attribute: Style(color="cyan"),
    Name.Tag: Style(color="bright_blue"),
    String: Style(color="yellow"),
    Number: Style(color="blue"),
    Generic.Deleted: Style(color="bright_red"),
    Generic.Inserted: Style(color="green"),
    Generic.Heading: Style(bold=True),
    Generic.Subheading: Style(color="magenta", bold=True),
    Generic.Prompt: Style(bold=True),
    Generic.Error: Style(color="bright_red"),
    Error: Style(color="red", underline=True),
}

ANSI_DARK: Dict[TokenType, Style] = {
    Token: Style(),
    Whitespace: Style(color="bright_black"),
    Comment: Style(dim=True),
    Comment.Preproc: Style(color="bright_cyan"),
    Keyword: Style(color="bright_blue"),
    Keyword.Type: Style(color="bright_cyan"),
    Operator.Word: Style(color="bright_magenta"),
    Name.Builtin: Style(color="bright_cyan"),
    Name.Function: Style(color="bright_green"),
    Name.Namespace: Style(color="bright_cyan", underline=True),
    Name.Class: Style(color="bright_green", underline=True),
    Name.Exception: Style(color="bright_cyan"),
    Name.Decorator: Style(color="bright_magenta", bold=True),
    Name.Variable: Style(color="bright_red"),
    Name.Constant: Style(color="bright_red"),
    Name.Attribute: Style(color="bright_cyan"),
    Name.Tag: Style(color="bright_blue"),
    String: Style(color="yellow"),
    Number: Style(color="bright_blue"),
    Generic.Deleted: Style(color="bright_red"),
    Generic.Inserted: Style(color="bright_green"),
    Generic.Heading: Style(bold=True),
    Generic.Subheading: Style(color="bright_magenta", bold=True),
    Generic.Prompt: Style(bold=True),
    Generic.Error: Style(color="bright_red"),
    Error: Style(color="red", underline=True),
}

RICH_SYNTAX_THEMES = {"ansi_light": ANSI_LIGHT, "ansi_dark": ANSI_DARK}
NUMBERS_COLUMN_DEFAULT_PADDING = 2

def _pygments_style_from_token(
    theme_self: Any, token_type: TokenType, pygments_style_class: Any
) -> Style:
    try:
        pygments_style = pygments_style_class.style_for_token(token_type)
    except KeyError:
        return Style.null()
    color = pygments_style["color"]
    bgcolor = pygments_style["bgcolor"]
    return Style(
        color="#" + color if color else "#000000",
        bgcolor="#" + bgcolor if bgcolor else theme_self._background_color,
        bold=pygments_style["bold"],
        italic=pygments_style["italic"],
        underline=pygments_style["underline"],
    )

def _pygments_style_for_token(
    theme_self: Any, token_type: TokenType
) -> Style:
    cached = theme_self._style_cache.get(token_type)
    if cached is not None:
        return cached
    style = _pygments_style_from_token(
        theme_self, token_type, theme_self._pygments_style_class
    )
    theme_self._style_cache[token_type] = style
    return style

def _pygments_syntax_theme_init(
    self, theme: Union[str, Type[PygmentsStyle]]
) -> None:
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

def _ansi_token_style(style_map: Dict[TokenType, Style], token_type: TokenType) -> Style:
    token = tuple(token_type)
    while token:
        style = style_map.get(token)
        if style is not None:
            return style
        token = token[:-1]
    return Style.null()

def _ansi_style_for_token(theme_self: Any, token_type: TokenType) -> Style:
    cached = theme_self._style_cache.get(token_type)
    if cached is not None:
        return cached
    style = _ansi_token_style(theme_self.style_map, token_type)
    theme_self._style_cache[token_type] = style
    return style

def _ansi_syntax_theme_init(self, style_map: Dict[TokenType, Style]) -> None:
    self.style_map = style_map
    self._missing_style = Style.null()
    self._background_style = Style.null()
    self._style_cache: Dict[TokenType, Style] = {}

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

PygmentsSyntaxTheme = type(
    "PygmentsSyntaxTheme",
    (SyntaxTheme,),
    {
        "__doc__": "Syntax theme that delegates to Pygments theme.",
        "__init__": _pygments_syntax_theme_init,
        "get_style_for_token": _pygments_style_for_token,
        "get_background_style": lambda self: self._background_style,
    },
)

ANSISyntaxTheme = type(
    "ANSISyntaxTheme",
    (SyntaxTheme,),
    {
        "__doc__": "Syntax theme to use standard colors.",
        "__init__": _ansi_syntax_theme_init,
        "get_style_for_token": _ansi_style_for_token,
        "get_background_style": lambda self: self._background_style,
    },
)

SyntaxPosition = Tuple[int, int]

def _syntax_highlight_range_new(
    cls,
    style: StyleType,
    start: SyntaxPosition,
    end: SyntaxPosition,
    style_before: bool = False,
):
    return tuple.__new__(cls, (style, start, end, style_before))

_SyntaxHighlightRange = type(
    "_SyntaxHighlightRange",
    (tuple,),
    {
        "__doc__": "A range to highlight in a Syntax object.",
        "__new__": _syntax_highlight_range_new,
        "style": property(lambda self: self[0]),
        "start": property(lambda self: self[1]),
        "end": property(lambda self: self[2]),
        "style_before": property(lambda self: self[3]),
    },
)

def _padding_property_get(
    self, obj: "Syntax", objtype: Type["Syntax"]
) -> Tuple[int, int, int, int]:
    return obj._padding

def _padding_property_set(
    self, obj: "Syntax", padding: PaddingDimensions
) -> None:
    obj._padding = Padding.unpack(padding)

PaddingProperty = type(
    "PaddingProperty",
    (),
    {
        "__doc__": "Descriptor to get and set padding.",
        "__get__": _padding_property_get,
        "__set__": _padding_property_set,
    },
)

def _syntax_highlight_line_range(
    syntax_self: "Syntax",
    code: str,
    line_range: Tuple[Optional[int], Optional[int]],
    _get_theme_style: Callable[[Any], Style],
) -> Iterable[Tuple[str, Optional[Style]]]:
    line_start, line_end = line_range
    lexer = syntax_self.lexer
    assert lexer is not None

    def line_tokenize() -> Iterable[Tuple[Any, str]]:
        for token_type, token in lexer.get_tokens(code):
            while token:
                line_token, new_line, token = token.partition("\n")
                yield token_type, line_token + new_line

    tokens = iter(line_tokenize())
    line_no = 0
    _line_start = line_start - 1 if line_start else 0
    while line_no < _line_start:
        try:
            _token_type, token = next(tokens)
        except StopIteration:
            return
        yield (token, None)
        if token.endswith("\n"):
            line_no += 1
    for token_type, token in tokens:
        yield (token, _get_theme_style(token_type))
        if token.endswith("\n"):
            line_no += 1
            if line_end and line_no >= line_end:
                break

def _syntax_indent_guide_style(syntax_self: "Syntax") -> Style:
    return (
        syntax_self._get_base_style()
        + syntax_self._theme.get_style_for_token(Comment)
        + Style(dim=True)
        + syntax_self.background_style
    )

def _syntax_render_simple(
    syntax_self: "Syntax",
    console: "Console",
    options: "ConsoleOptions",
    code_width: int,
    ends_on_nl: bool,
    text: Text,
) -> Iterable[Segment]:
    if not ends_on_nl:
        text.remove_suffix("\n")
    style = _syntax_indent_guide_style(syntax_self)
    if syntax_self.indent_guides and not options.ascii_only:
        text = text.with_indent_guides(syntax_self.tab_size, style=style)
        text.overflow = "crop"
    if style.transparent_background:
        yield from console.render(text, options=options.update(width=code_width))
        return
    syntax_lines = console.render_lines(
        text,
        options.update(width=code_width, height=None, justify="left"),
        style=syntax_self.background_style,
        pad=True,
        new_lines=True,
    )
    for syntax_line in syntax_lines:
        yield from syntax_line

def _syntax_prepare_lines(
    syntax_self: "Syntax",
    text: Text,
    ends_on_nl: bool,
    options: "ConsoleOptions",
) -> Tuple[Union[List[Text], Lines], int]:
    start_line, end_line = syntax_self.line_range or (None, None)
    line_offset = max(0, start_line - 1) if start_line else 0
    lines: Union[List[Text], Lines] = text.split("\n", allow_blank=ends_on_nl)
    if syntax_self.line_range:
        if line_offset > len(lines):
            return [], line_offset
        lines = lines[line_offset:end_line]
    if syntax_self.indent_guides and not options.ascii_only:
        style = _syntax_indent_guide_style(syntax_self)
        lines = (
            Text("\n")
            .join(lines)
            .with_indent_guides(
                syntax_self.tab_size, style=style + Style(italic=False)
            )
            .split("\n", allow_blank=True)
        )
    return lines, line_offset

def _syntax_wrap_line(
    syntax_self: "Syntax",
    console: "Console",
    line: Text,
    render_options: "ConsoleOptions",
    background_style: Style,
    transparent_background: bool,
    no_wrap: bool,
) -> List[List[Segment]]:
    if syntax_self.word_wrap:
        return console.render_lines(
            line,
            render_options.update(height=None, justify="left"),
            style=background_style,
            pad=not transparent_background,
        )
    segments = list(line.render(console, end=""))
    if no_wrap:
        return [segments]
    return [
        Segment.adjust_line_length(
            segments,
            render_options.max_width,
            style=background_style,
            pad=not transparent_background,
        )
    ]

def _syntax_numbered_line_prefix(
    line_no: int,
    *,
    numbers_column_width: int,
    highlight: bool,
    line_pointer: str,
    highlight_number_style: Style,
    number_style: Style,
) -> Iterable[Segment]:
    line_column = str(line_no).rjust(numbers_column_width - 2) + " "
    if highlight:
        yield Segment(line_pointer, Style(color="red"))
        yield Segment(line_column, highlight_number_style)
        return
    yield Segment("  ", highlight_number_style)
    yield Segment(line_column, number_style)

def _syntax_yield_numbered_wrapped_lines(
    wrapped_lines: List[List[Segment]],
    line_no: int,
    *,
    numbers_column_width: int,
    background_style: Style,
    number_style: Style,
    highlight_number_style: Style,
    line_pointer: str,
    highlight: bool,
    new_line: Segment,
) -> Iterable[Segment]:
    wrapped_line_left_pad = Segment(" " * numbers_column_width + " ", background_style)
    for first, wrapped_line in loop_first(wrapped_lines):
        if first:
            yield from _syntax_numbered_line_prefix(
                line_no,
                numbers_column_width=numbers_column_width,
                highlight=highlight,
                line_pointer=line_pointer,
                highlight_number_style=highlight_number_style,
                number_style=number_style,
            )
        else:
            yield wrapped_line_left_pad
        yield from wrapped_line
        yield new_line

def _syntax_yield_wrapped_line(
    wrapped_lines: List[List[Segment]],
    line_no: int,
    *,
    line_numbers: bool,
    numbers_column_width: int,
    background_style: Style,
    number_style: Style,
    highlight_number_style: Style,
    line_pointer: str,
    highlight: bool,
    new_line: Segment,
) -> Iterable[Segment]:
    if line_numbers:
        yield from _syntax_yield_numbered_wrapped_lines(
            wrapped_lines,
            line_no,
            numbers_column_width=numbers_column_width,
            background_style=background_style,
            number_style=number_style,
            highlight_number_style=highlight_number_style,
            line_pointer=line_pointer,
            highlight=highlight,
            new_line=new_line,
        )
        return
    for wrapped_line in wrapped_lines:
        yield from wrapped_line
        yield new_line

def _get_code_index_for_syntax_position(
    newlines_offsets: Sequence[int], position: SyntaxPosition
) -> Optional[int]:
    lines_count = len(newlines_offsets)
    line_number, column_index = position
    if line_number > lines_count or len(newlines_offsets) < (line_number + 1):
        return None
    line_index = line_number - 1
    line_length = newlines_offsets[line_index + 1] - newlines_offsets[line_index] - 1
    column_index = min(line_length, column_index)
    return newlines_offsets[line_index] + column_index

def _syntax_apply_stylized_range(
    text: Text,
    newlines_offsets: Sequence[int],
    stylized_range: Any,
) -> None:
    start = _get_code_index_for_syntax_position(newlines_offsets, stylized_range.start)
    end = _get_code_index_for_syntax_position(newlines_offsets, stylized_range.end)
    if start is None or end is None:
        return
    if stylized_range.style_before:
        text.stylize_before(stylized_range.style, start, end)
    else:
        text.stylize(stylized_range.style, start, end)

class Syntax(JupyterMixin):
    """Construct a Syntax object to render syntax highlighted code.

    Args:
        code (str): Code to highlight.
        lexer (Lexer | str): Lexer to use (see https://pygments.org/docs/lexers/)
        theme (str, optional): Color theme, aka Pygments style (see https://pygments.org/docs/styles/#getting-a-list-of-available-styles). Defaults to "monokai".
        dedent (bool, optional): Enable stripping of initial whitespace. Defaults to False.
        line_numbers (bool, optional): Enable rendering of line numbers. Defaults to False.
        start_line (int, optional): Starting number for line numbers. Defaults to 1.
        line_range (Tuple[int | None, int | None], optional): If given should be a tuple of the start and end line to render.
            A value of None in the tuple indicates the range is open in that direction.
        highlight_lines (Set[int]): A set of line numbers to highlight.
        code_width: Width of code to render (not including line numbers), or ``None`` to use all available width.
        tab_size (int, optional): Size of tabs. Defaults to 4.
        word_wrap (bool, optional): Enable word wrapping.
        background_color (str, optional): Optional background color, or None to use theme color. Defaults to None.
        indent_guides (bool, optional): Show indent guides. Defaults to False.
        padding (PaddingDimensions): Padding to apply around the syntax. Defaults to 0 (no padding).
    """

    _pygments_style_class: Type[PygmentsStyle]
    _theme: SyntaxTheme

    @classmethod
    def get_theme(cls, name: Union[str, SyntaxTheme]) -> SyntaxTheme:
        """Get a syntax theme instance."""
        if isinstance(name, SyntaxTheme):
            return name
        theme: SyntaxTheme
        if name in RICH_SYNTAX_THEMES:
            theme = ANSISyntaxTheme(RICH_SYNTAX_THEMES[name])
        else:
            theme = PygmentsSyntaxTheme(name)
        return theme

    def __init__(
        self,
        code: str,
        lexer: Union[Lexer, str],
        *,
        theme: Union[str, SyntaxTheme] = DEFAULT_THEME,
        dedent: bool = False,
        line_numbers: bool = False,
        start_line: int = 1,
        line_range: Optional[Tuple[Optional[int], Optional[int]]] = None,
        highlight_lines: Optional[Set[int]] = None,
        code_width: Optional[int] = None,
        tab_size: int = 4,
        word_wrap: bool = False,
        background_color: Optional[str] = None,
        indent_guides: bool = False,
        padding: PaddingDimensions = 0,
    ) -> None:
        self.code = code
        self._lexer = lexer
        self.dedent = dedent
        self.line_numbers = line_numbers
        self.start_line = start_line
        self.line_range = line_range
        self.highlight_lines = highlight_lines or set()
        self.code_width = code_width
        self.tab_size = tab_size
        self.word_wrap = word_wrap
        self.background_color = background_color
        self.background_style = (
            Style(bgcolor=background_color) if background_color else Style()
        )
        self.indent_guides = indent_guides
        self._padding = Padding.unpack(padding)

        self._theme = self.get_theme(theme)
        self._stylized_ranges: List[_SyntaxHighlightRange] = []

    padding = PaddingProperty()

    @classmethod
    def from_path(
        cls,
        path: str,
        encoding: str = "utf-8",
        lexer: Optional[Union[Lexer, str]] = None,
        theme: Union[str, SyntaxTheme] = DEFAULT_THEME,
        dedent: bool = False,
        line_numbers: bool = False,
        line_range: Optional[Tuple[int, int]] = None,
        start_line: int = 1,
        highlight_lines: Optional[Set[int]] = None,
        code_width: Optional[int] = None,
        tab_size: int = 4,
        word_wrap: bool = False,
        background_color: Optional[str] = None,
        indent_guides: bool = False,
        padding: PaddingDimensions = 0,
    ) -> "Syntax":
        """Construct a Syntax object from a file.

        Args:
            path (str): Path to file to highlight.
            encoding (str): Encoding of file.
            lexer (str | Lexer, optional): Lexer to use. If None, lexer will be auto-detected from path/file content.
            theme (str, optional): Color theme, aka Pygments style (see https://pygments.org/docs/styles/#getting-a-list-of-available-styles). Defaults to "emacs".
            dedent (bool, optional): Enable stripping of initial whitespace. Defaults to True.
            line_numbers (bool, optional): Enable rendering of line numbers. Defaults to False.
            start_line (int, optional): Starting number for line numbers. Defaults to 1.
            line_range (Tuple[int, int], optional): If given should be a tuple of the start and end line to render.
            highlight_lines (Set[int]): A set of line numbers to highlight.
            code_width: Width of code to render (not including line numbers), or ``None`` to use all available width.
            tab_size (int, optional): Size of tabs. Defaults to 4.
            word_wrap (bool, optional): Enable word wrapping of code.
            background_color (str, optional): Optional background color, or None to use theme color. Defaults to None.
            indent_guides (bool, optional): Show indent guides. Defaults to False.
            padding (PaddingDimensions): Padding to apply around the syntax. Defaults to 0 (no padding).

        Returns:
            [Syntax]: A Syntax object that may be printed to the console
        """
        code = Path(path).read_text(encoding=encoding)

        if not lexer:
            lexer = cls.guess_lexer(path, code=code)

        return cls(
            code,
            lexer,
            theme=theme,
            dedent=dedent,
            line_numbers=line_numbers,
            line_range=line_range,
            start_line=start_line,
            highlight_lines=highlight_lines,
            code_width=code_width,
            tab_size=tab_size,
            word_wrap=word_wrap,
            background_color=background_color,
            indent_guides=indent_guides,
            padding=padding,
        )

    @classmethod
    def guess_lexer(cls, path: str, code: Optional[str] = None) -> str:
        """Guess the alias of the Pygments lexer to use based on a path and an optional string of code.
        If code is supplied, it will use a combination of the code and the filename to determine the
        best lexer to use. For example, if the file is ``index.html`` and the file contains Django
        templating syntax, then "html+django" will be returned. If the file is ``index.html``, and no
        templating language is used, the "html" lexer will be used. If no string of code
        is supplied, the lexer will be chosen based on the file extension..

        Args:
            path (AnyStr): The path to the file containing the code you wish to know the lexer for.
            code (str, optional): Optional string of code that will be used as a fallback if no lexer
                is found for the supplied path.

        Returns:
            str: The name of the Pygments lexer that best matches the supplied path/code.
        """
        lexer: Optional[Lexer] = None
        lexer_name = "default"
        if code:
            try:
                lexer = guess_lexer_for_filename(path, code)
            except ClassNotFound:
                pass

        if not lexer:
            try:
                _, ext = os.path.splitext(path)
                if ext:
                    extension = ext.lstrip(".").lower()
                    lexer = get_lexer_by_name(extension)
            except ClassNotFound:
                pass

        if lexer:
            if lexer.aliases:
                lexer_name = lexer.aliases[0]
            else:
                lexer_name = lexer.name
            if lexer_name.lower() == "ipython" and path.endswith(".py"):
                lexer_name = "python"

        return lexer_name

    def _get_base_style(self) -> Style:
        """Get the base style."""
        default_style = self._theme.get_background_style() + self.background_style
        return default_style

    def _get_token_color(self, token_type: TokenType) -> Optional[Color]:
        """Get a color (if any) for the given token.

        Args:
            token_type (TokenType): A token type tuple from Pygments.

        Returns:
            Optional[Color]: Color from theme, or None for no color.
        """
        style = self._theme.get_style_for_token(token_type)
        return style.color

    @property
    def lexer(self) -> Optional[Lexer]:
        """The lexer for this syntax, or None if no lexer was found.

        Tries to find the lexer by name if a string was passed to the constructor.
        """

        if isinstance(self._lexer, Lexer):
            return self._lexer
        try:
            return get_lexer_by_name(
                self._lexer,
                stripnl=False,
                ensurenl=True,
                tabsize=self.tab_size,
            )
        except ClassNotFound:
            return None

    @property
    def default_lexer(self) -> Lexer:
        """A Pygments Lexer to use if one is not specified or invalid."""
        return get_lexer_by_name(
            "text",
            stripnl=False,
            ensurenl=True,
            tabsize=self.tab_size,
        )

    def highlight(
        self,
        code: str,
        line_range: Optional[Tuple[Optional[int], Optional[int]]] = None,
    ) -> Text:
        """Highlight code and return a Text instance.

        Args:
            code (str): Code to highlight.
            line_range(Tuple[int, int], optional): Optional line range to highlight.

        Returns:
            Text: A text instance containing highlighted syntax.
        """

        base_style = self._get_base_style()
        justify: JustifyMethod = (
            "default" if base_style.transparent_background else "left"
        )

        text = Text(
            justify=justify,
            style=base_style,
            tab_size=self.tab_size,
            no_wrap=not self.word_wrap,
        )
        _get_theme_style = self._theme.get_style_for_token

        lexer = self.lexer or self.default_lexer

        if lexer is None:
            text.append(code)
        elif line_range:
            text.append_tokens(
                _syntax_highlight_line_range(self, code, line_range, _get_theme_style)
            )
        else:
            text.append_tokens(
                (token, _get_theme_style(token_type))
                for token_type, token in lexer.get_tokens(code)
            )
        if self.background_color is not None:
            text.stylize(f"on {self.background_color}")

        if self._stylized_ranges:
            self._apply_stylized_ranges(text)

        return text

    def stylize_range(
        self,
        style: StyleType,
        start: SyntaxPosition,
        end: SyntaxPosition,
        style_before: bool = False,
    ) -> None:
        """
        Adds a custom style on a part of the code, that will be applied to the syntax display when it's rendered.
        Line numbers are 1-based, while column indexes are 0-based.

        Args:
            style (StyleType): The style to apply.
            start (Tuple[int, int]): The start of the range, in the form `[line number, column index]`.
            end (Tuple[int, int]): The end of the range, in the form `[line number, column index]`.
            style_before (bool): Apply the style before any existing styles.
        """
        self._stylized_ranges.append(
            _SyntaxHighlightRange(style, start, end, style_before)
        )

    def _get_line_numbers_color(self, blend: float = 0.3) -> Color:
        background_style = self._theme.get_background_style() + self.background_style
        background_color = background_style.bgcolor
        if background_color is None or background_color.is_system_defined:
            return Color.default()
        foreground_color = self._get_token_color(Token.Text)
        if foreground_color is None or foreground_color.is_system_defined:
            return foreground_color or Color.default()
        new_color = blend_rgb(
            background_color.get_truecolor(),
            foreground_color.get_truecolor(),
            cross_fade=blend,
        )
        return Color.from_triplet(new_color)

    @property
    def _numbers_column_width(self) -> int:
        """Get the number of characters used to render the numbers column."""
        column_width = 0
        if self.line_numbers:
            column_width = (
                len(str(self.start_line + self.code.count("\n")))
                + NUMBERS_COLUMN_DEFAULT_PADDING
            )
        return column_width

    def _get_number_styles(self, console: Console) -> Tuple[Style, Style, Style]:
        """Get background, number, and highlight styles for line numbers."""
        background_style = self._get_base_style()
        if background_style.transparent_background:
            return Style.null(), Style(dim=True), Style.null()
        if console.color_system in ("256", "truecolor"):
            number_style = Style.chain(
                background_style,
                self._theme.get_style_for_token(Token.Text),
                Style(color=self._get_line_numbers_color()),
                self.background_style,
            )
            highlight_number_style = Style.chain(
                background_style,
                self._theme.get_style_for_token(Token.Text),
                Style(bold=True, color=self._get_line_numbers_color(0.9)),
                self.background_style,
            )
        else:
            number_style = background_style + Style(dim=True)
            highlight_number_style = background_style + Style(dim=False)
        return background_style, number_style, highlight_number_style

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        _, right, _, left = self.padding
        padding = left + right
        if self.code_width is not None:
            width = self.code_width + self._numbers_column_width + padding + 1
            return Measurement(self._numbers_column_width, width)
        lines = self.code.splitlines()
        width = (
            self._numbers_column_width
            + padding
            + (max(cell_len(line) for line in lines) if lines else 0)
        )
        if self.line_numbers:
            width += 1
        return Measurement(self._numbers_column_width, width)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        segments = Segments(self._get_syntax(console, options))
        if any(self.padding):
            yield Padding(segments, style=self._get_base_style(), pad=self.padding)
        else:
            yield segments

    def _get_syntax(
        self,
        console: Console,
        options: ConsoleOptions,
    ) -> Iterable[Segment]:
        """
        Get the Segments for the Syntax object, excluding any vertical/horizontal padding
        """
        transparent_background = self._get_base_style().transparent_background
        _pad_top, pad_right, _pad_bottom, pad_left = self.padding
        horizontal_padding = pad_left + pad_right
        code_width = (
            (
                (options.max_width - self._numbers_column_width - 1)
                if self.line_numbers
                else options.max_width
            )
            - horizontal_padding
            if self.code_width is None
            else self.code_width
        )
        code_width = max(0, code_width)

        ends_on_nl, processed_code = self._process_code(self.code)
        text = self.highlight(processed_code, self.line_range)

        if not self.line_numbers and not self.word_wrap and not self.line_range:
            yield from _syntax_render_simple(
                self, console, options, code_width, ends_on_nl, text
            )
            return

        lines, line_offset = _syntax_prepare_lines(self, text, ends_on_nl, options)
        if not lines and self.line_range:
            return

        render_options = options.update(width=code_width)
        highlight_line = self.highlight_lines.__contains__
        new_line = Segment("\n")
        line_pointer = "> " if options.legacy_windows else "❱ "
        background_style, number_style, highlight_number_style = self._get_number_styles(
            console
        )

        for line_no, line in enumerate(lines, self.start_line + line_offset):
            wrapped_lines = _syntax_wrap_line(
                self,
                console,
                line,
                render_options,
                background_style,
                transparent_background,
                options.no_wrap,
            )
            yield from _syntax_yield_wrapped_line(
                wrapped_lines,
                line_no,
                line_numbers=self.line_numbers,
                numbers_column_width=self._numbers_column_width,
                background_style=background_style,
                number_style=number_style,
                highlight_number_style=highlight_number_style,
                line_pointer=line_pointer,
                highlight=highlight_line(line_no),
                new_line=new_line,
            )

    def _apply_stylized_ranges(self, text: Text) -> None:
        """
        Apply stylized ranges to a text instance,
        using the given code to determine the right portion to apply the style to.

        Args:
            text (Text): Text instance to apply the style to.
        """
        code = text.plain
        newlines_offsets = [
            # Let's add outer boundaries at each side of the list:
            0,
            # N.B. using "\n" here is much faster than using metacharacters such as "^" or "\Z":
            *[
                match.start() + 1
                for match in re.finditer("\n", code, flags=re.MULTILINE)
            ],
            len(code) + 1,
        ]

        for stylized_range in self._stylized_ranges:
            _syntax_apply_stylized_range(text, newlines_offsets, stylized_range)

    def _process_code(self, code: str) -> Tuple[bool, str]:
        """
        Applies various processing to a raw code string
        (normalises it so it always ends with a line return, dedents it if necessary, etc.)

        Args:
            code (str): The raw code string to process

        Returns:
            Tuple[bool, str]: the boolean indicates whether the raw code ends with a line return,
                while the string is the processed code.
        """
        ends_on_nl = code.endswith("\n")
        processed_code = code if ends_on_nl else code + "\n"
        processed_code = (
            textwrap.dedent(processed_code) if self.dedent else processed_code
        )
        processed_code = processed_code.expandtabs(self.tab_size)
        return ends_on_nl, processed_code

if __name__ == "__main__":  # pragma: no cover
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Render syntax to the console with Rich"
    )
    parser.add_argument(
        "path",
        metavar="PATH",
        help="path to file, or - for stdin",
    )
    parser.add_argument(
        "-c",
        "--force-color",
        dest="force_color",
        action="store_true",
        default=None,
        help="force color for non-terminals",
    )
    parser.add_argument(
        "-i",
        "--indent-guides",
        dest="indent_guides",
        action="store_true",
        default=False,
        help="display indent guides",
    )
    parser.add_argument(
        "-l",
        "--line-numbers",
        dest="line_numbers",
        action="store_true",
        help="render line numbers",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        dest="width",
        default=None,
        help="width of output (default will auto-detect)",
    )
    parser.add_argument(
        "-r",
        "--wrap",
        dest="word_wrap",
        action="store_true",
        default=False,
        help="word wrap long lines",
    )
    parser.add_argument(
        "-s",
        "--soft-wrap",
        action="store_true",
        dest="soft_wrap",
        default=False,
        help="enable soft wrapping mode",
    )
    parser.add_argument(
        "-t", "--theme", dest="theme", default="monokai", help="pygments theme"
    )
    parser.add_argument(
        "-b",
        "--background-color",
        dest="background_color",
        default=None,
        help="Override background color",
    )
    parser.add_argument(
        "-x",
        "--lexer",
        default=None,
        dest="lexer_name",
        help="Lexer name",
    )
    parser.add_argument(
        "-p", "--padding", type=int, default=0, dest="padding", help="Padding"
    )
    parser.add_argument(
        "--highlight-line",
        type=int,
        default=None,
        dest="highlight_line",
        help="The line number (not index!) to highlight",
    )
    args = parser.parse_args()

    import importlib

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    Console = importlib.import_module(_pkg + ".console").Console

    console = Console(force_terminal=args.force_color, width=args.width)

    if args.path == "-":
        code = sys.stdin.read()
        syntax = Syntax(
            code=code,
            lexer=args.lexer_name,
            line_numbers=args.line_numbers,
            word_wrap=args.word_wrap,
            theme=args.theme,
            background_color=args.background_color,
            indent_guides=args.indent_guides,
            padding=args.padding,
            highlight_lines={args.highlight_line},
        )
    else:
        syntax = Syntax.from_path(
            args.path,
            lexer=args.lexer_name,
            line_numbers=args.line_numbers,
            word_wrap=args.word_wrap,
            theme=args.theme,
            background_color=args.background_color,
            indent_guides=args.indent_guides,
            padding=args.padding,
            highlight_lines={args.highlight_line},
        )
    console.print(syntax, soft_wrap=args.soft_wrap)