import importlib
from typing import Any, Iterable, List

from ._jupyter_renderable import JupyterMixin, JupyterRenderable

__all__ = ["JupyterMixin", "JupyterRenderable", "display", "get_console", "jupyter_print", "print"]


def _get_console():
    return importlib.import_module(".".join(["rich", "_console_state"])).obtain_shared_console()


get_console = _get_console


def _segment_type() -> type:
    return importlib.import_module(".".join(["rich", "segment"])).Segment


def _default_terminal_theme():
    return importlib.import_module(".".join(["rich", "terminal_theme"])).DEFAULT_TERMINAL_THEME


JUPYTER_HTML_FORMAT = """\
<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">{code}</pre>
"""


def _render_segments(segments: Iterable[Any]) -> str:
    def escape(text: str) -> str:
        """Escape html."""
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    fragments: List[str] = []
    append_fragment = fragments.append
    theme = _default_terminal_theme()
    for text, style, control in _segment_type().simplify(segments):
        if control:
            continue
        text = escape(text)
        if style:
            rule = style.get_html_style(theme)
            text = f'<span style="{rule}">{text}</span>' if rule else text
            if style.link:
                text = f'<a href="{style.link}" target="_blank">{text}</a>'
        append_fragment(text)

    code = "".join(fragments)
    html = JUPYTER_HTML_FORMAT.format(code=code)

    return html


def display(segments: Iterable[Any], text: str) -> None:
    """Render segments to Jupyter."""
    html = _render_segments(segments)
    jupyter_renderable = JupyterRenderable(html, text)
    try:
        from IPython.display import display as ipython_display

        ipython_display(jupyter_renderable)
    except ModuleNotFoundError:
        # Handle the case where the Console has force_jupyter=True,
        # but IPython is not installed.
        pass


def jupyter_print(*args: Any, **kwargs: Any) -> None:
    """Proxy for Console print."""
    console = get_console()
    return console.print(*args, **kwargs)


print = jupyter_print
