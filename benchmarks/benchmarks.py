from io import StringIO

from benchmarks import snippets


def _rich(name: str):
    import importlib

    return importlib.import_module(f"rich.{name}")


class TextSuite:
    def setup(self):
        Console = _rich("console").Console
        Text = _rich("text").Text
        self.console = Console(
            file=StringIO(), color_system="truecolor", legacy_windows=False
        )
        self.len_lorem_ipsum = len(snippets.LOREM_IPSUM)
        self.text = Text.from_markup(snippets.MARKUP)

    def time_wrapping(self):
        self.text.wrap(self.console, 12, overflow="fold")

    def time_indent_guides(self):
        Text = _rich("text").Text
        Text(snippets.PYTHON_SNIPPET).with_indent_guides()

    def time_fit(self):
        Text = _rich("text").Text
        Text(snippets.LOREM_IPSUM).fit(12)

    def time_split(self):
        self.text.split()

    def time_divide(self):
        Text = _rich("text").Text
        Text(snippets.LOREM_IPSUM).divide(range(20, 100, 4))

    def time_align_center(self):
        Text = _rich("text").Text
        Text(snippets.LOREM_IPSUM).align("center", width=self.len_lorem_ipsum * 3)

    def time_render(self):
        list(self.text.render(self.console))

    def time_wrapping_unicode_heavy(self):
        Text = _rich("text").Text
        Text(snippets.UNICODE_HEAVY_TEXT).wrap(self.console, 12, overflow="fold")

    def time_fit_unicode_heavy(self):
        Text = _rich("text").Text
        Text(snippets.UNICODE_HEAVY_TEXT).fit(12)

    def time_split_unicode_heavy(self):
        Text = _rich("text").Text
        Text(snippets.UNICODE_HEAVY_TEXT).split()

    def time_divide_unicode_heavy(self):
        self.text.divide(range(20, 100, 4))

    def time_align_center_unicode_heavy(self):
        Text = _rich("text").Text
        Text(snippets.UNICODE_HEAVY_TEXT).align(
            "center", width=self.len_lorem_ipsum * 3
        )

    def time_render_unicode_heavy(self):
        Text = _rich("text").Text
        list(Text(snippets.UNICODE_HEAVY_TEXT).render(self.console))


_benchmark_aux_namespace: dict = {
    "StringIO": StringIO,
    "snippets": snippets,
    "_rich": _rich,
}
exec(
    '''
class TextHotCacheSuite:
    def setup(self):
        Console = _rich("console").Console
        self.console = Console(
            file=StringIO(), color_system="truecolor", legacy_windows=False
        )

    def time_wrapping_unicode_heavy_warm_cache(self):
        Text = _rich("text").Text
        for _ in range(20):
            Text(snippets.UNICODE_HEAVY_TEXT).wrap(self.console, 12, overflow="fold")


class SyntaxWrappingSuite:
    def setup(self):
        Console = _rich("console").Console
        Syntax = _rich("syntax").Syntax
        self.console = Console(
            file=StringIO(), color_system="truecolor", legacy_windows=False
        )
        self.syntax = Syntax(
            code=snippets.PYTHON_SNIPPET, lexer="python", word_wrap=True
        )

    def time_text_thin_terminal_heavy_wrapping(self):
        self._print_with_width(20)

    def time_text_thin_terminal_medium_wrapping(self):
        self._print_with_width(60)

    def time_text_wide_terminal_no_wrapping(self):
        self._print_with_width(100)

    def _print_with_width(self, width):
        self.console.print(self.syntax, width)


class TableSuite:
    def time_table_no_wrapping(self):
        self._print_table(width=100)

    def time_table_heavy_wrapping(self):
        self._print_table(width=30)

    def _print_table(self, width):
        Table = _rich("table").Table
        Console = _rich("console").Console
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


class PrettySuite:
    def setup(self):
        Console = _rich("console").Console
        self.console = Console(
            file=StringIO(), color_system="truecolor", legacy_windows=False, width=100
        )

    def time_pretty(self):
        Pretty = _rich("pretty").Pretty
        pretty = Pretty(snippets.PYTHON_DICT)
        self.console.print(pretty)

    def time_pretty_indent_guides(self):
        Pretty = _rich("pretty").Pretty
        pretty = Pretty(snippets.PYTHON_DICT, indent_guides=True)
        self.console.print(pretty)

    def time_pretty_justify_center(self):
        Pretty = _rich("pretty").Pretty
        pretty = Pretty(snippets.PYTHON_DICT, justify="center")
        self.console.print(pretty)


class StyleSuite:
    def setup(self):
        Console = _rich("console").Console
        Style = _rich("style").Style
        self.console = Console(
            file=StringIO(), color_system="truecolor", legacy_windows=False, width=100
        )
        self.style1 = Style.parse("blue on red")
        self.style2 = Style.parse("green italic bold")

    def time_parse_ansi(self):
        Style = _rich("style").Style
        Style.parse("red on blue")

    def time_parse_hex(self):
        Style = _rich("style").Style
        Style.parse("#f0f0f0 on #e2e28a")

    def time_parse_mixed_complex_style(self):
        Style = _rich("style").Style
        Style.parse("dim bold reverse #00ee00 on rgb(123,12,50)")

    def time_style_add(self):
        self.style1 + self.style2


class ColorSuite:
    def setup(self):
        Console = _rich("console").Console
        Color = _rich("color").Color
        self.console = Console(
            file=StringIO(), color_system="truecolor", legacy_windows=False, width=100
        )
        self.color = Color.parse("#0d1da0")

    def time_downgrade_to_eight_bit(self):
        ColorSystem = _rich("color").ColorSystem
        self.color.downgrade(ColorSystem.EIGHT_BIT)

    def time_downgrade_to_standard(self):
        ColorSystem = _rich("color").ColorSystem
        self.color.downgrade(ColorSystem.STANDARD)

    def time_downgrade_to_windows(self):
        ColorSystem = _rich("color").ColorSystem
        self.color.downgrade(ColorSystem.WINDOWS)


class ColorSuiteCached:
    def setup(self):
        Console = _rich("console").Console
        Color = _rich("color").Color
        ColorSystem = _rich("color").ColorSystem
        self.console = Console(
            file=StringIO(), color_system="truecolor", legacy_windows=False, width=100
        )
        self.color = Color.parse("#0d1da0")
        self.color.downgrade(ColorSystem.EIGHT_BIT)
        self.color.downgrade(ColorSystem.STANDARD)
        self.color.downgrade(ColorSystem.WINDOWS)

    def time_downgrade_to_eight_bit(self):
        ColorSystem = _rich("color").ColorSystem
        self.color.downgrade(ColorSystem.EIGHT_BIT)

    def time_downgrade_to_standard(self):
        ColorSystem = _rich("color").ColorSystem
        self.color.downgrade(ColorSystem.STANDARD)

    def time_downgrade_to_windows(self):
        ColorSystem = _rich("color").ColorSystem
        self.color.downgrade(ColorSystem.WINDOWS)


class SegmentSuite:
    def setup(self):
        Segment = _rich("segment").Segment
        self.line = [
            Segment("foo"),
            Segment("bar"),
            Segment("egg"),
            Segment("Where there is a Will"),
            Segment("There is a way"),
        ] * 2

    def test_divide_complex(self):
        Segment = _rich("segment").Segment
        list(Segment.divide(self.line, [5, 10, 20, 50, 108, 110, 118]))
''',
    _benchmark_aux_namespace,
)
TextHotCacheSuite = _benchmark_aux_namespace["TextHotCacheSuite"]
SyntaxWrappingSuite = _benchmark_aux_namespace["SyntaxWrappingSuite"]
TableSuite = _benchmark_aux_namespace["TableSuite"]
PrettySuite = _benchmark_aux_namespace["PrettySuite"]
StyleSuite = _benchmark_aux_namespace["StyleSuite"]
ColorSuite = _benchmark_aux_namespace["ColorSuite"]
ColorSuiteCached = _benchmark_aux_namespace["ColorSuiteCached"]
SegmentSuite = _benchmark_aux_namespace["SegmentSuite"]
