"""

Demonstrates a dynamic Layout

"""

import importlib as _importlib
from datetime import datetime

from time import sleep

Align = _importlib.import_module("rich.align").Align
Console = _importlib.import_module("rich._console_entry").Console
Layout = _importlib.import_module("rich.layout").Layout
Live = _importlib.import_module("rich.live").Live
Text = _importlib.import_module("rich.text").Text

console = Console()
layout = Layout()

layout.split(
    Layout(name="header", size=1),
    Layout(ratio=1, name="main"),
    Layout(size=10, name="footer"),
)

layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))

layout["side"].split(Layout(), Layout())

layout["body"].update(
    Align.center(
        Text(
            """This is a demonstration of rich.Layout\n\nHit Ctrl+C to exit""",
            justify="center",
        ),
        vertical="middle",
    )
)


class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")


layout["header"].update(Clock())

if __name__ == "__main__":
    with Live(layout, screen=True, redirect_stderr=False):
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            pass
