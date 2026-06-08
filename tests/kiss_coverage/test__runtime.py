"""Kiss static coverage for rich._runtime."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._runtime

def test_kiss__runtime_symbols_0():
    _mod = _import_rich('_runtime')
    get_align_class = getattr(_mod, 'get_align_class')
    get_console_class = getattr(_mod, 'get_console_class')
    get_console_renderable = getattr(_mod, 'get_console_renderable')
    get_global_console = getattr(_mod, 'get_global_console')
    get_panel_class = getattr(_mod, 'get_panel_class')
    get_panel_module = getattr(_mod, 'get_panel_module')
    get_pretty_class = getattr(_mod, 'get_pretty_class')
    get_pretty_module = getattr(_mod, 'get_pretty_module')
    assert get_align_class is not None
    assert get_console_class is not None
    assert get_console_renderable is not None
    assert get_global_console is not None
    assert get_panel_class is not None
    assert get_panel_module is not None
    assert get_pretty_class is not None
    assert get_pretty_module is not None

def test_kiss__runtime_symbols_1():
    _mod = _import_rich('_runtime')
    get_render_scope = getattr(_mod, 'get_render_scope')
    get_repr_highlighter = getattr(_mod, 'get_repr_highlighter')
    get_rich = getattr(_mod, 'get_rich')
    get_rule_class = getattr(_mod, 'get_rule_class')
    get_scope_module = getattr(_mod, 'get_scope_module')
    get_segment_class = getattr(_mod, 'get_segment_class')
    get_status_class = getattr(_mod, 'get_status_class')
    get_syntax_class = getattr(_mod, 'get_syntax_class')
    assert get_render_scope is not None
    assert get_repr_highlighter is not None
    assert get_rich is not None
    assert get_rule_class is not None
    assert get_scope_module is not None
    assert get_segment_class is not None
    assert get_status_class is not None
    assert get_syntax_class is not None

def test_kiss__runtime_symbols_2():
    _mod = _import_rich('_runtime')
    get_table_class = getattr(_mod, 'get_table_class')
    get_text_class = getattr(_mod, 'get_text_class')
    get_traceback_class = getattr(_mod, 'get_traceback_class')
    assert get_table_class is not None
    assert get_text_class is not None
    assert get_traceback_class is not None
