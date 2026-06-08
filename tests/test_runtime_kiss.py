"""Kiss coverage for rich._runtime lazy module lookups."""

from rich._runtime import (
    _mod,
    get_align_class,
    get_global_console,
    get_console_class,
    get_panel_class,
    get_panel_module,
    get_pretty_class,
    get_pretty_module,
    get_render_scope,
    get_repr_highlighter,
    get_rich,
    get_rule_class,
    get_scope_module,
    get_segment_class,
    get_status_class,
    get_syntax_class,
    get_table_class,
    get_text_class,
    get_traceback_class,
)


def test_runtime_lazy_lookups():
    assert get_rich() is _mod("rich")
    assert get_global_console() is not None
    assert get_console_class() is _mod("rich.console").Console
    assert get_segment_class() is _mod("rich.segment").Segment
    assert get_text_class() is _mod("rich.text").Text
    assert get_pretty_class() is _mod("rich.pretty").Pretty
    assert get_panel_class() is _mod("rich.panel").Panel
    assert get_syntax_class() is _mod("rich.syntax").Syntax
    assert get_repr_highlighter() is _mod("rich.highlighter").ReprHighlighter
    assert get_render_scope() is _mod("rich.scope").render_scope
    assert get_table_class() is _mod("rich.table").Table
    assert get_status_class() is _mod("rich.status").Status
    assert get_align_class() is _mod("rich.align").Align
    assert get_rule_class() is _mod("rich.rule").Rule
    assert get_traceback_class() is _mod("rich.traceback").Traceback
    assert get_pretty_module() is _mod("rich.pretty")
    assert get_panel_module() is _mod("rich.panel")
    assert get_scope_module() is _mod("rich.scope")
