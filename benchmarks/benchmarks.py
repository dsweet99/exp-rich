from io import StringIO

from benchmarks import snippets
from rich.color import Color, ColorSystem
from rich.console import Console
from rich.pretty import Pretty
from rich.segment import Segment
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text


def _text_suite_setup(self):
    self.console = Console(
        file=StringIO(), color_system="truecolor", legacy_windows=False
    )
    self.len_lorem_ipsum = len(snippets.LOREM_IPSUM)
    self.text = Text.from_markup(snippets.MARKUP)


def _text_suite_time_wrapping(self):
    self.text.wrap(self.console, 12, overflow="fold")


def _text_suite_time_indent_guides(self):
    Text(snippets.PYTHON_SNIPPET).with_indent_guides()


def _text_suite_time_fit(self):
    Text(snippets.LOREM_IPSUM).fit(12)


def _text_suite_time_split(self):
    self.text.split()


def _text_suite_time_divide(self):
    Text(snippets.LOREM_IPSUM).divide(range(20, 100, 4))


def _text_suite_time_align_center(self):
    Text(snippets.LOREM_IPSUM).align("center", width=self.len_lorem_ipsum * 3)


def _text_suite_time_render(self):
    list(self.text.render(self.console))


def _text_suite_time_wrapping_unicode_heavy(self):
    Text(snippets.UNICODE_HEAVY_TEXT).wrap(self.console, 12, overflow="fold")


def _text_suite_time_fit_unicode_heavy(self):
    Text(snippets.UNICODE_HEAVY_TEXT).fit(12)


def _text_suite_time_split_unicode_heavy(self):
    Text(snippets.UNICODE_HEAVY_TEXT).split()


def _text_suite_time_divide_unicode_heavy(self):
    self.text.divide(range(20, 100, 4))


def _text_suite_time_align_center_unicode_heavy(self):
    Text(snippets.UNICODE_HEAVY_TEXT).align(
        "center", width=self.len_lorem_ipsum * 3
    )


def _text_suite_time_render_unicode_heavy(self):
    list(Text(snippets.UNICODE_HEAVY_TEXT).render(self.console))


TextSuite = type(
    "TextSuite",
    (),
    {
        "setup": _text_suite_setup,
        "time_wrapping": _text_suite_time_wrapping,
        "time_indent_guides": _text_suite_time_indent_guides,
        "time_fit": _text_suite_time_fit,
        "time_split": _text_suite_time_split,
        "time_divide": _text_suite_time_divide,
        "time_align_center": _text_suite_time_align_center,
        "time_render": _text_suite_time_render,
        "time_wrapping_unicode_heavy": _text_suite_time_wrapping_unicode_heavy,
        "time_fit_unicode_heavy": _text_suite_time_fit_unicode_heavy,
        "time_split_unicode_heavy": _text_suite_time_split_unicode_heavy,
        "time_divide_unicode_heavy": _text_suite_time_divide_unicode_heavy,
        "time_align_center_unicode_heavy": _text_suite_time_align_center_unicode_heavy,
        "time_render_unicode_heavy": _text_suite_time_render_unicode_heavy,
    },
)


def _text_hot_cache_setup(self):
    self.console = Console(
        file=StringIO(), color_system="truecolor", legacy_windows=False
    )


def _text_hot_cache_time_wrapping(self):
    for _ in range(20):
        Text(snippets.UNICODE_HEAVY_TEXT).wrap(self.console, 12, overflow="fold")


TextHotCacheSuite = type(
    "TextHotCacheSuite",
    (),
    {"setup": _text_hot_cache_setup, "time_wrapping_unicode_heavy_warm_cache": _text_hot_cache_time_wrapping},
)


def _syntax_setup(self):
    self.console = Console(
        file=StringIO(), color_system="truecolor", legacy_windows=False
    )
    self.syntax = Syntax(code=snippets.PYTHON_SNIPPET, lexer="python", word_wrap=True)


def _syntax_print_with_width(self, width):
    self.console.print(self.syntax, width)


def _syntax_time_thin(self):
    _syntax_print_with_width(self, 20)


def _syntax_time_medium(self):
    _syntax_print_with_width(self, 60)


def _syntax_time_wide(self):
    _syntax_print_with_width(self, 100)


SyntaxWrappingSuite = type(
    "SyntaxWrappingSuite",
    (),
    {
        "setup": _syntax_setup,
        "_print_with_width": _syntax_print_with_width,
        "time_text_thin_terminal_heavy_wrapping": _syntax_time_thin,
        "time_text_thin_terminal_medium_wrapping": _syntax_time_medium,
        "time_text_wide_terminal_no_wrapping": _syntax_time_wide,
    },
)


def _table_print(self, width):
    table = Table(title="Star Wars Movies")
    console = Console(
        file=StringIO(), color_system="truecolor", legacy_windows=False, width=width
    )
    table.add_column("Released", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Box Office", justify="right", style="green")
    table.add_row(
        "Dec 20, 2019", "[b]Star Wars[/]: The Rise of Skywalker", "$952,110,690"
    )
    table.add_row(
        "May 25, 2018", "Solo: A [red][b]Star Wars[/] Story[/]", "$393,151,347"
    )
    table.add_row(
        "Dec 15, 2017",
        "[b red]Star Wars[/] Ep. V111: The Last Jedi",
        "$1,332,539,889",
    )
    table.add_row(
        "Dec 16, 2016", "Rogue One: A [blue]Star Wars[/] Story", "$1,332,439,889"
    )
    console.print(table)


TableSuite = type(
    "TableSuite",
    (),
    {
        "time_table_no_wrapping": lambda self: _table_print(self, 100),
        "time_table_heavy_wrapping": lambda self: _table_print(self, 30),
        "_print_table": _table_print,
    },
)


def _pretty_setup(self):
    self.console = Console(
        file=StringIO(), color_system="truecolor", legacy_windows=False, width=100
    )


def _pretty_time_pretty(self):
    self.console.print(Pretty(snippets.PYTHON_DICT))


def _pretty_time_indent(self):
    self.console.print(Pretty(snippets.PYTHON_DICT, indent_guides=True))


def _pretty_time_justify(self):
    self.console.print(Pretty(snippets.PYTHON_DICT, justify="center"))


PrettySuite = type(
    "PrettySuite",
    (),
    {
        "setup": _pretty_setup,
        "time_pretty": _pretty_time_pretty,
        "time_pretty_indent_guides": _pretty_time_indent,
        "time_pretty_justify_center": _pretty_time_justify,
    },
)


def _style_setup(self):
    self.console = Console(
        file=StringIO(), color_system="truecolor", legacy_windows=False, width=100
    )
    self.style1 = Style.parse("blue on red")
    self.style2 = Style.parse("green italic bold")


StyleSuite = type(
    "StyleSuite",
    (),
    {
        "setup": _style_setup,
        "time_parse_ansi": lambda self: Style.parse("red on blue"),
        "time_parse_hex": lambda self: Style.parse("#f0f0f0 on #e2e28a"),
        "time_parse_mixed_complex_style": lambda self: Style.parse(
            "dim bold reverse #00ee00 on rgb(123,12,50)"
        ),
        "time_style_add": lambda self: self.style1 + self.style2,
    },
)


def _color_setup(self):
    self.console = Console(
        file=StringIO(), color_system="truecolor", legacy_windows=False, width=100
    )
    self.color = Color.parse("#0d1da0")


def _color_setup_cached(self):
    _color_setup(self)
    self.color.downgrade(ColorSystem.EIGHT_BIT)
    self.color.downgrade(ColorSystem.STANDARD)
    self.color.downgrade(ColorSystem.WINDOWS)


ColorSuite = type(
    "ColorSuite",
    (),
    {
        "setup": _color_setup,
        "time_downgrade_to_eight_bit": lambda self: self.color.downgrade(
            ColorSystem.EIGHT_BIT
        ),
        "time_downgrade_to_standard": lambda self: self.color.downgrade(
            ColorSystem.STANDARD
        ),
        "time_downgrade_to_windows": lambda self: self.color.downgrade(
            ColorSystem.WINDOWS
        ),
    },
)

ColorSuiteCached = type(
    "ColorSuiteCached",
    (),
    {
        "setup": _color_setup_cached,
        "time_downgrade_to_eight_bit": lambda self: self.color.downgrade(
            ColorSystem.EIGHT_BIT
        ),
        "time_downgrade_to_standard": lambda self: self.color.downgrade(
            ColorSystem.STANDARD
        ),
        "time_downgrade_to_windows": lambda self: self.color.downgrade(
            ColorSystem.WINDOWS
        ),
    },
)


def _segment_setup(self):
    self.line = [
        Segment("foo"),
        Segment("bar"),
        Segment("egg"),
        Segment("Where there is a Will"),
        Segment("There is a way"),
    ] * 2


SegmentSuite = type(
    "SegmentSuite",
    (),
    {
        "setup": _segment_setup,
        "test_divide_complex": lambda self: list(
            Segment.divide(self.line, [5, 10, 20, 50, 108, 110, 118])
        ),
    },
)
