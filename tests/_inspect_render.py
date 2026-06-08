"""Inspect test render helper (lazy rich imports for kiss)."""
from __future__ import annotations

import importlib as _importlib
import io


def render(obj, methods=False, value=False, width=50) -> str:
    inspect = _importlib.import_module("rich").inspect
    Console = _importlib.import_module("rich._console_entry").Console
    console = Console(file=io.StringIO(), width=width, legacy_windows=False)
    inspect(obj, console=console, methods=methods, value=value)
    return console.file.getvalue()


def inspect_module():
    return _importlib.import_module("rich").inspect


def console_class():
    return _importlib.import_module("rich._console_entry").Console


def get_object_types_mro(obj):
    return _importlib.import_module("rich._inspect").get_object_types_mro(obj)


def get_object_types_mro_as_strings(obj):
    return _importlib.import_module("rich._inspect").get_object_types_mro_as_strings(obj)


def is_object_one_of_types(obj, types):
    return _importlib.import_module("rich._inspect").is_object_one_of_types(obj, types)
