"""Smoke-test ASV benchmark suites without timing assertions."""

from __future__ import annotations


def _smoke_text_suite(TextSuite) -> None:
    text = TextSuite()
    text.setup()
    text.time_wrapping()
    text.time_indent_guides()
    text.time_fit()
    text.time_split()
    text.time_divide()
    text.time_align_center()
    text.time_render()
    text.time_wrapping_unicode_heavy()
    text.time_fit_unicode_heavy()
    text.time_split_unicode_heavy()
    text.time_divide_unicode_heavy()
    text.time_align_center_unicode_heavy()
    text.time_render_unicode_heavy()


def _smoke_hot_cache_suite(TextHotCacheSuite) -> None:
    hot = TextHotCacheSuite()
    hot.setup()
    hot.time_wrapping_unicode_heavy_warm_cache()


def _smoke_syntax_suite(SyntaxWrappingSuite) -> None:
    syntax = SyntaxWrappingSuite()
    syntax.setup()
    syntax.time_text_thin_terminal_heavy_wrapping()
    syntax.time_text_thin_terminal_medium_wrapping()
    syntax.time_text_wide_terminal_no_wrapping()


def _smoke_table_suite(TableSuite) -> None:
    table = TableSuite()
    table.time_table_no_wrapping()
    table.time_table_heavy_wrapping()


def _smoke_pretty_suite(PrettySuite) -> None:
    pretty = PrettySuite()
    pretty.setup()
    pretty.time_pretty()
    pretty.time_pretty_indent_guides()
    pretty.time_pretty_justify_center()


def _smoke_style_suite(StyleSuite) -> None:
    style = StyleSuite()
    style.setup()
    style.time_parse_ansi()
    style.time_parse_hex()
    style.time_parse_mixed_complex_style()
    style.time_style_add()


def _smoke_color_suite(ColorSuite) -> None:
    color = ColorSuite()
    color.setup()
    color.time_downgrade_to_eight_bit()
    color.time_downgrade_to_standard()
    color.time_downgrade_to_windows()


def _smoke_color_cached_suite(ColorSuiteCached) -> None:
    cached = ColorSuiteCached()
    cached.setup()
    cached.time_downgrade_to_eight_bit()
    cached.time_downgrade_to_standard()
    cached.time_downgrade_to_windows()


def _smoke_segment_suite(SegmentSuite) -> None:
    segment = SegmentSuite()
    segment.setup()
    segment.test_divide_complex()


def test_benchmark_suites_smoke():
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

    _smoke_text_suite(TextSuite)
    _smoke_hot_cache_suite(TextHotCacheSuite)
    _smoke_syntax_suite(SyntaxWrappingSuite)
    _smoke_table_suite(TableSuite)
    _smoke_pretty_suite(PrettySuite)
    _smoke_style_suite(StyleSuite)
    _smoke_color_suite(ColorSuite)
    _smoke_color_cached_suite(ColorSuiteCached)
    _smoke_segment_suite(SegmentSuite)
