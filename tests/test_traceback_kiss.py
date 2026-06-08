"""Kiss static references for rich.traceback."""

import io

import pytest
from rich.console import Console
from rich.traceback import (
    Stack as TracebackStack,
    install as traceback_install,
    traceback_example_bar,
    traceback_example_foo,
)


def test_traceback_examples():
    traceback_install(console=Console(file=io.StringIO()))
    assert TracebackStack is not None
    with pytest.raises(ZeroDivisionError):
        traceback_example_foo(0)
    with pytest.raises(ZeroDivisionError):
        traceback_example_bar(0)
