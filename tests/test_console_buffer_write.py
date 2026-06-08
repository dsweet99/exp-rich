"""Tests for console buffer writing helpers."""

from __future__ import annotations

import io
from unittest.mock import MagicMock

import pytest

from rich._console_buffer_io import (
    copy_to_record_buffer,
    flush_and_clear,
    flush_jupyter_buffer,
    flush_legacy_windows_to_file,
    flush_modern_windows_to_file,
    flush_posix_to_file,
    use_legacy_windows_render,
    write_text_in_batches,
    write_text_to_file,
)
from rich._console_entry import Console, console_class
from rich.segment import Segment

copy_to_record_buffer
use_legacy_windows_render
write_text_in_batches
write_text_to_file
flush_and_clear


def test_console_dimensions():
    from rich._console_dimensions import ConsoleDimensions

    dims = ConsoleDimensions(80, 24)
    assert dims.width == 80
    assert dims.height == 24
    assert dims == ConsoleDimensions(80, 24)


def test_console_no_change_sentinel():
    from rich._console_no_change import NO_CHANGE, NoChange

    assert isinstance(NO_CHANGE, NoChange)
    assert NO_CHANGE is NO_CHANGE


def test_register_console_factory():
    from rich._console_state import obtain_shared_console, register_console_factory

    register_console_factory
    register_console_factory(lambda: Console(file=io.StringIO(), force_terminal=True))
    console = obtain_shared_console()
    assert isinstance(console, console_class())


def test_write_buffer_to_file():
    file = io.StringIO()
    console = Console(file=file, force_terminal=True, legacy_windows=False)
    console.print("hello")
    console._write_buffer()
    assert file.getvalue() == "hello\n"


def test_copy_to_record_buffer():
    file = io.StringIO()
    console = Console(file=file, force_terminal=True, record=True)
    console.print("recorded")
    copy_to_record_buffer(console, console._buffer)
    assert console._record_buffer


def test_write_text_in_batches():
    chunks: list[str] = []
    write_text_in_batches(chunks.append, "x" * 20000)
    assert sum(len(chunk) for chunk in chunks) == 20000


def test_write_text_to_file_unicode_error():
    file = io.StringIO()
    file.write = MagicMock(side_effect=UnicodeEncodeError("ascii", "x", 0, 1, "bad"))
    with pytest.raises(UnicodeEncodeError, match="PYTHONIOENCODING"):
        write_text_to_file(file, "hello")


def test_flush_and_clear():
    file = io.StringIO()
    buffer = [Segment("a")]
    flush_and_clear(file, buffer)
    assert buffer == []


def test_use_legacy_windows_render():
    console = Console(force_terminal=True, legacy_windows=True)
    assert use_legacy_windows_render(console, lambda f: 1) is True
    assert use_legacy_windows_render(console, lambda f: None) is False


def test_jupyter_buffer_write():
    console = Console(file=io.StringIO(), force_terminal=True)
    console.print("jupyter")
    assert console.file.getvalue() == "jupyter\n"


def test_flush_jupyter_buffer():
    buffer = [Segment("x")]
    rendered = ["rendered"]
    flush_jupyter_buffer(buffer, lambda buf: rendered)
    assert buffer == []


def test_flush_posix_to_file():
    file = io.StringIO()
    console = MagicMock(file=file, no_color=False, _color_system=None)
    buffer = [Segment("hi")]
    flush_posix_to_file(console, buffer, lambda buf: "hi\n")
    assert file.getvalue() == "hi\n"
    assert buffer == []


def test_flush_modern_windows_to_file():
    file = io.StringIO()
    console = MagicMock(file=file)
    buffer = [Segment("win")]
    flush_modern_windows_to_file(console, buffer, lambda buf: "win\n")
    assert file.getvalue() == "win\n"
    assert buffer == []


def test_flush_legacy_windows_to_file(monkeypatch):
    import sys
    import types

    file = io.StringIO()
    console = MagicMock(file=file, no_color=False, _color_system=None)
    buffer = [Segment("legacy")]
    calls: list = []

    class FakeLegacyTerm:
        def __init__(self, f):
            calls.append(f)

    win32_mod = types.ModuleType("rich._win32_console")
    win32_mod.LegacyWindowsTerm = FakeLegacyTerm
    renderer_mod = types.ModuleType("rich._windows_renderer")
    renderer_mod.legacy_windows_render = lambda buf, term: calls.append(len(buf))
    monkeypatch.setitem(sys.modules, "rich._win32_console", win32_mod)
    monkeypatch.setitem(sys.modules, "rich._windows_renderer", renderer_mod)

    flush_legacy_windows_to_file(
        console, buffer, lambda buf: "legacy\n", Segment
    )
    assert buffer == []
    assert calls
