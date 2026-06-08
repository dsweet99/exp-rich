import io
from time import process_time

from ._test_card import ColorBox, make_test_card

if __name__ == "__main__":  # pragma: no cover
    import importlib

    Console = getattr(importlib.import_module("rich." + "console"), "Console")
    Panel = getattr(importlib.import_module("rich." + "panel"), "Panel")

    console = Console(
        file=io.StringIO(),
        force_terminal=True,
    )
    test_card = make_test_card()

    start = process_time()
    console.print(test_card)
    pre_cache_taken = round((process_time() - start) * 1000.0, 1)

    console.file = io.StringIO()

    start = process_time()
    console.print(test_card)
    taken = round((process_time() - start) * 1000.0, 1)

    c = Console(record=True)
    c.print(test_card)

    console = Console()
    console.print(f"[dim]rendered in [not dim]{pre_cache_taken}ms[/] (cold cache)")
    console.print(f"[dim]rendered in [not dim]{taken}ms[/] (warm cache)")
    console.print()
    console.print(
        Panel(
            "[b magenta]Hope you enjoy using Rich![/]\n\n"
            "Consider sponsoring to ensure this project is maintained.\n\n"
            "[cyan]https://github.com/sponsors/willmcgugan[/cyan]",
            border_style="green",
            title="Help ensure Rich is maintained",
            padding=(1, 2),
        )
    )
