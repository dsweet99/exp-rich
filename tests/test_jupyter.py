from __future__ import annotations

from unittest.mock import patch

from rich._console_entry import Console
from rich.jupyter import JupyterMixin, JupyterRenderable, display, jupyter_print
from rich.segment import Segment


def test_jupyter():
    console = Console(force_jupyter=True)
    assert console.width == 115
    assert console.height == 100
    assert console.color_system == "truecolor"


def test_jupyter_columns_env():
    console = Console(_environ={"JUPYTER_COLUMNS": "314"}, force_jupyter=True)
    assert console.width == 314
    # width take precedence
    console = Console(width=40, _environ={"JUPYTER_COLUMNS": "314"}, force_jupyter=True)
    assert console.width == 40
    # Should not fail
    console = Console(
        width=40, _environ={"JUPYTER_COLUMNS": "broken"}, force_jupyter=True
    )


def test_jupyter_lines_env():
    console = Console(_environ={"JUPYTER_LINES": "220"}, force_jupyter=True)
    assert console.height == 220
    # height take precedence
    console = Console(height=40, _environ={"JUPYTER_LINES": "220"}, force_jupyter=True)
    assert console.height == 40
    # Should not fail
    console = Console(
        width=40, _environ={"JUPYTER_LINES": "broken"}, force_jupyter=True
    )


def test_jupyter_renderable_mimebundle() -> None:
    renderable = JupyterRenderable("<b>hi</b>", "hi")
    assert renderable.html == "<b>hi</b>"
    assert renderable.text == "hi"
    assert renderable._repr_mimebundle_((), ()) == {
        "text/plain": "hi",
        "text/html": "<b>hi</b>",
    }
    assert renderable._repr_mimebundle_(("text/plain",), ()) == {"text/plain": "hi"}
    assert renderable._repr_mimebundle_((), ("text/html",)) == {"text/plain": "hi"}


class _JupyterDemo(JupyterMixin):
    def __rich_console__(self, console, options):
        yield Segment("hello")


def test_jupyter_mixin_mimebundle() -> None:
    demo = _JupyterDemo()
    bundle = demo._repr_mimebundle_((), ())
    assert bundle["text/plain"] == "hello"
    assert "hello" in bundle["text/html"]


def test_jupyter_print() -> None:
    console = Console()
    with patch("rich.jupyter.get_console", return_value=console), patch.object(
        console, "print", return_value=None
    ) as mock_print:
        jupyter_print("hello")
    mock_print.assert_called_once_with("hello")


def test_jupyter_display_without_ipython() -> None:
    segments = [Segment("x")]
    with patch.dict("sys.modules", {"IPython.display": None}):
        display(segments, "x")
