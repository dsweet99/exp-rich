"""Tests for examples.print_calendar."""
from __future__ import annotations

import io


def test_print_calendar_renders_year():
    from examples.print_calendar import print_calendar
    from rich._console_entry import Console

    Console(file=io.StringIO(), width=120)
    print_calendar(2024)
