from rich import print
from rich._console_entry import group
from rich.panel import Panel


@group()
def get_panels():
    yield Panel("Hello", style="on blue")
    yield Panel("World", style="on red")


if __name__ == "__main__":
    print(Panel(get_panels()))
