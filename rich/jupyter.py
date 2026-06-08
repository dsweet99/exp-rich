from typing import Any


def display(segments: Any, text: str) -> None:
    """Render segments to Jupyter."""
    from ._console_write import segments_to_styled_parts
    from ._jupyter_html import display_html, render_styled_parts

    html = render_styled_parts(segments_to_styled_parts(segments))
    display_html(html, text)


def print(*args: Any, **kwargs: Any) -> None:
    """Proxy for Console print."""
    from .console import get_console

    return get_console().print(*args, **kwargs)


def __getattr__(name: str) -> Any:
    if name == "JupyterMixin":
        from ._jupyter_mixin import JupyterMixin

        return JupyterMixin
    if name == "JupyterRenderable":
        from ._jupyter_html import JupyterRenderable

        return JupyterRenderable
    if name == "render_mimebundle":
        from ._console_write import render_mimebundle

        return render_mimebundle
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
