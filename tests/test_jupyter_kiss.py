"""Kiss static reference for rich.jupyter.print."""

from rich.jupyter import jupyter_rich_print


def test_jupyter_print():
    jupyter_rich_print({"kiss": True})
