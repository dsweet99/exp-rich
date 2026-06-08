from __future__ import annotations

from ._lazy import import_attr, import_submodule
import os
import platform

inspect = import_submodule('rich.inspect')
Console = import_attr('rich.console', 'Console')
get_windows_console_features = import_attr('rich.console', 'get_windows_console_features')
Panel = import_attr('rich.panel', 'Panel')
Pretty = import_attr('rich.pretty', 'Pretty')


def report() -> None:  # pragma: no cover
    """Print a report to the terminal with debugging information"""
    console = Console()
    inspect(console)
    features = get_windows_console_features()
    inspect(features)

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
