"""Kiss static references for rich.abc."""

from rich.abc import AbcExampleFoo, RichRenderable


def test_abc_example_foo():
    assert isinstance(AbcExampleFoo(), RichRenderable) is False
    assert RichRenderable is not None
