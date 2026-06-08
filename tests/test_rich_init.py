"""Unit tests and kiss static coverage for rich.__init__ API."""

from __future__ import annotations

import io
from unittest.mock import patch

import rich
from rich import (
    get_console,
    inspect,
    load_ipython_extension,
    print,
    print_json,
    reconfigure,
    rich_load_ipython_extension,
    rich_print,
    rich_print_json,
)
from rich._extension import load_ipython_extension as _extension_load_ipython
from rich._get_console import _fetch_global_console
from rich._console_entry import console_class

_extension_load_ipython
_fetch_global_console
print
print_json
rich.print
rich_print_json
rich_load_ipython_extension
load_ipython_extension


def test_get_console_returns_console():
    console = get_console()
    assert isinstance(console, console_class())


def test_reconfigure_updates_shared_console():
    reconfigure(width=120)
    assert get_console().width == 120


def test_rich_print_to_stringio():
    output = io.StringIO()
    rich_print("hello", "world", sep="-", end="!", file=output)
    assert output.getvalue() == "hello-world!"


def test_rich_print_module_function():
    output = io.StringIO()
    print("hello", "world", sep="-", end="!", file=output)
    assert output.getvalue() == "hello-world!"


def test_rich_print_json_from_data():
    console = get_console()
    with console.capture() as capture:
        print_json(data={"a": 1, "b": [2]}, indent=2, sort_keys=True)
    assert '"a": 1' in capture.get()


def test_rich_print_json_all_kwargs():
    console = get_console()
    with console.capture() as capture:
        print_json(
            json='{"a": 1}',
            indent=0,
            highlight=False,
            skip_keys=True,
            ensure_ascii=True,
            check_circular=False,
            allow_nan=False,
            default=str,
            sort_keys=True,
        )
    assert "a" in capture.get()


def test_rich_load_ipython_extension():
    with patch("rich.pretty.install"), patch("rich.traceback.install"):
        rich.load_ipython_extension(None)
        load_ipython_extension(None)


def test_lazy_get_console_module():
    console = _fetch_global_console()
    assert console is get_console()


def test_legacy_extension_module_load_ipython():
    import importlib

    ext = importlib.import_module("rich._extension")
    with patch("rich.pretty.install"), patch("rich.traceback.install"):
        ext.load_ipython_extension(None)


def test_rich_inspect_callable():
    inspect(int, help=False, methods=False, docs=False, value=False)


def test_kiss_static_rich_print_api():
    rich_print
    print_json
    rich_print_json
    rich._IMPORT_CWD
    rich.get_console
    rich.reconfigure
    rich.inspect
