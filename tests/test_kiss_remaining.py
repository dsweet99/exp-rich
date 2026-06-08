"""Behavioral tests for rich._stack (not in .kissignore)."""

from __future__ import annotations

import io


def test_stack_push_and_top():
    from rich._stack import Stack, _Stack

    stack = _Stack([1])
    stack.push(2)
    assert stack.top == 2
    assert isinstance(Stack(), _Stack)


def test_ansi_registry_register_and_lookup():
    import importlib as _importlib

    registry = _importlib.import_module("rich._ansi_registry")
    ansi = _importlib.import_module("rich.ansi")
    registry.register_ansi_decoder(ansi.AnsiDecoder)
    assert registry.ansi_decoder_class() is ansi.AnsiDecoder


def test_console_entry_register_and_class():
    import importlib as _importlib

    entry = _importlib.import_module("rich._console_entry")
    console_mod = _importlib.import_module("rich.console")
    entry.register_console_class(console_mod.Console)
    cls = entry.console_class()
    assert cls is console_mod.Console
    instance = cls(file=io.StringIO(), width=80)
    assert instance.width == 80


def test_logging_entry_register_and_class():
    import importlib as _importlib

    entry = _importlib.import_module("rich._logging_entry")
    logging_mod = _importlib.import_module("rich.logging")
    entry.register_rich_handler_class(logging_mod.RichHandler)
    cls = entry.rich_handler_class()
    assert cls is logging_mod.RichHandler
    handler = cls()
    assert handler.markup is False
