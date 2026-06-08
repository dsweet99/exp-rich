"""Smoke tests for ASV benchmark suites."""

from benchmarks.benchmarks import (
    ColorSuite,
    ColorSuiteCached,
    PrettySuite,
    SegmentSuite,
    StyleSuite,
    SyntaxWrappingSuite,
    TableSuite,
    TextHotCacheSuite,
    TextSuite,
)


def test_text_suite_benchmarks():
    suite = TextSuite()
    suite.setup()
    suite.time_wrapping()
    suite.time_indent_guides()
    suite.time_fit()
    suite.time_split()
    suite.time_divide()
    suite.time_align_center()
    suite.time_render()
    suite.time_wrapping_unicode_heavy()
    suite.time_fit_unicode_heavy()
    suite.time_split_unicode_heavy()
    suite.time_divide_unicode_heavy()
    suite.time_align_center_unicode_heavy()
    suite.time_render_unicode_heavy()


def test_text_hot_cache_suite():
    suite = TextHotCacheSuite()
    suite.setup()
    suite.time_wrapping_unicode_heavy_warm_cache()


def test_syntax_wrapping_suite():
    suite = SyntaxWrappingSuite()
    suite.setup()
    suite.time_text_thin_terminal_heavy_wrapping()
    suite.time_text_thin_terminal_medium_wrapping()
    suite.time_text_wide_terminal_no_wrapping()


def test_table_suite():
    suite = TableSuite()
    suite.time_table_no_wrapping()
    suite.time_table_heavy_wrapping()


def test_pretty_suite():
    suite = PrettySuite()
    suite.setup()
    suite.time_pretty()
    suite.time_pretty_indent_guides()
    suite.time_pretty_justify_center()


def test_style_suite():
    suite = StyleSuite()
    suite.setup()
    suite.time_parse_ansi()
    suite.time_parse_hex()
    suite.time_parse_mixed_complex_style()
    suite.time_style_add()


def test_color_suites():
    for suite_cls in (ColorSuite, ColorSuiteCached):
        suite = suite_cls()
        suite.setup()
        suite.time_downgrade_to_eight_bit()
        suite.time_downgrade_to_standard()
        suite.time_downgrade_to_windows()


def test_segment_suite():
    suite = SegmentSuite()
    suite.setup()
    suite.test_divide_complex()
