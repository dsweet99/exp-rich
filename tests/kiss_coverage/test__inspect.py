"""Kiss static coverage for rich._inspect."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich._inspect

def test_kiss__inspect_symbols_0():
    _mod = _import_rich('_inspect')
    Inspect = getattr(_mod, 'Inspect')
    get_object_types_mro = getattr(_mod, 'get_object_types_mro')
    get_object_types_mro_as_strings = getattr(_mod, 'get_object_types_mro_as_strings')
    is_object_one_of_types = getattr(_mod, 'is_object_one_of_types')
    render_inspect = getattr(_mod, 'render_inspect')
    assert Inspect is not None
    assert get_object_types_mro is not None
    assert get_object_types_mro_as_strings is not None
    assert is_object_one_of_types is not None
    assert render_inspect is not None
