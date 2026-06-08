from typing import Any, Dict, Iterable, List, Sequence

JUPYTER_HTML_FORMAT = """\
<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">{code}</pre>
"""


class JupyterRenderable:
    """A shim to write html to Jupyter notebook."""

    def __init__(self, html: str, text: str) -> None:
        self.html = html
        self.text = text

    def _repr_mimebundle_(
        self, include: Sequence[str], exclude: Sequence[str], **kwargs: Any
    ) -> Dict[str, str]:
        data = {"text/plain": self.text, "text/html": self.html}
        if include:
            data = {k: v for (k, v) in data.items() if k in include}
        if exclude:
            data = {k: v for (k, v) in data.items() if k not in exclude}
        return data


def _render_jupyter_html(segments: Iterable["Segment"]) -> str:
    import sys

    Segment = sys.modules["rich.segment"].Segment
    theme = sys.modules["rich.terminal_theme"].DEFAULT_TERMINAL_THEME
    fragments: List[str] = []
    for text, style, control in Segment.simplify(segments):
        if control:
            continue
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if style:
            rule = style.get_html_style(theme)
            text = f'<span style="{rule}">{text}</span>' if rule else text
            if style.link:
                text = f'<a href="{style.link}" target="_blank">{text}</a>'
        fragments.append(text)
    return JUPYTER_HTML_FORMAT.format(code="".join(fragments))


def repr_mimebundle_for_object(
    obj: Any,
    include: Sequence[str],
    exclude: Sequence[str],
    **kwargs: Any,
) -> Dict[str, str]:
    """Build a Jupyter mime bundle for a Rich renderable."""
    from . import get_console

    console = get_console()
    segments = list(console.render(obj, console.options))
    html = _render_jupyter_html(segments)
    text = console._render_buffer(segments)
    data = {"text/plain": text, "text/html": html}
    if include:
        data = {k: v for (k, v) in data.items() if k in include}
    if exclude:
        data = {k: v for (k, v) in data.items() if k not in exclude}
    return data


def _render_segments(segments: Iterable["Segment"]) -> str:
    return _render_jupyter_html(segments)


def display(segments: Iterable["Segment"], text: str) -> None:
    """Render segments to Jupyter."""
    html = _render_segments(segments)
    jupyter_renderable = JupyterRenderable(html, text)
    try:
        from IPython.display import display as ipython_display

        ipython_display(jupyter_renderable)
    except ModuleNotFoundError:
        pass


def jupyter_rich_print(*args: Any, **kwargs: Any) -> None:
    """Proxy for Console print."""
    from . import get_console

    console = get_console()
    return console.print(*args, **kwargs)


print = jupyter_rich_print
