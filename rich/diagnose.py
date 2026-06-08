import os
import platform

from ._pick import M_PRETTY, rich_module

from .console import Console, get_windows_console_features
from .panel import Panel


def report() -> None:  # pragma: no cover
    """Print a report to the terminal with debugging information"""
    from . import inspect as rich_inspect

    console = Console()
    rich_inspect(console)
    features = get_windows_console_features()
    rich_inspect(features)

    Pretty = rich_module(M_PRETTY).Pretty
    env_names = (
        "CLICOLOR",
        "COLORTERM",
        "COLUMNS",
        "JPY_PARENT_PID",
        "JUPYTER_COLUMNS",
        "JUPYTER_LINES",
        "LINES",
        "NO_COLOR",
        "TERM_PROGRAM",
        "TERM",
        "TTY_COMPATIBLE",
        "TTY_INTERACTIVE",
        "VSCODE_VERBOSE_LOGGING",
    )
    env = {name: os.getenv(name) for name in env_names}
    console.print(Panel.fit((Pretty(env)), title="[b]Environment Variables"))

    console.print(f'platform="{platform.system()}"')


if __name__ == "__main__":  # pragma: no cover
    report()
