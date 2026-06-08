"""Kiss symbol coverage for rich.jupyter and JupyterMixin."""

from rich._jupyter_mixin import JupyterMixin
from rich.jupyter import (
    JupyterRenderable,
    display,
    print as jupyter_print,
    repr_mimebundle_for_object,
)
from rich.text import Text


class _MixinExample(JupyterMixin):
    def __rich_console__(self, console, options):
        yield from console.render(Text("mixin"), options)


def test_kiss_jupyter_symbols():
    assert JupyterRenderable is not None
    assert JupyterMixin is not None
    assert display is not None
    assert jupyter_print is not None
    jupyter_print({"kiss": True})


def test_kiss_jupyter_mimebundle():
    bundle = JupyterRenderable("<b>x</b>", "x")._repr_mimebundle_([], [])
    assert bundle["text/plain"] == "x"
    assert "x" in bundle["text/html"]

    text = Text("hello")
    data = repr_mimebundle_for_object(text, [], [])
    assert "hello" in data["text/plain"]


def test_kiss_jupyter_mixin():
    data = _MixinExample()._repr_mimebundle_([], [])
    assert "mixin" in data["text/plain"]
    assert "mixin" in data["text/html"]

    include_only = _MixinExample()._repr_mimebundle_(["text/html"], [])
    assert set(include_only.keys()) == {"text/html"}

    exclude_html = _MixinExample()._repr_mimebundle_([], ["text/html"])
    assert "text/html" not in exclude_html
