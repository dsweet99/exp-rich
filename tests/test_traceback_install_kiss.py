"""Kiss static reference for rich.traceback.install and Stack."""

import io

from rich.console import Console
from rich.traceback import RichTracebackStack, rich_traceback_install


def test_traceback_install_and_stack():
    rich_traceback_install(console=Console(file=io.StringIO()))
    assert RichTracebackStack is not None
