from typing import Any, Dict, Iterable, Optional, Sequence, Tuple

StyledPart = Tuple[str, Optional[str], Optional[str]]


def _jupyter_renderable_init(self, html: str, text: str) -> None:
    self.html = html
    self.text = text


def _jupyter_renderable_repr_mimebundle(
    self, include: Sequence[str], exclude: Sequence[str], **kwargs: Any
) -> Dict[str, str]:
    data = {"text/plain": self.text, "text/html": self.html}
    if include:
        data = {k: v for (k, v) in data.items() if k in include}
    if exclude:
        data = {k: v for (k, v) in data.items() if k not in exclude}
    return data


JupyterRenderable = type(
    "JupyterRenderable",
    (),
    {
        "__doc__": "A shim to write html to Jupyter notebook.",
        "__init__": _jupyter_renderable_init,
        "_repr_mimebundle_": _jupyter_renderable_repr_mimebundle,
    },
)

JUPYTER_HTML_FORMAT = """\
<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">{code}</pre>
"""


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_styled_parts(parts: Iterable[StyledPart]) -> str:
    """Render pre-serialized styled parts to Jupyter HTML."""
    fragments = []
    append_fragment = fragments.append
    for text, rule, link in parts:
        text = _escape(text)
        if rule:
            text = f'<span style="{rule}">{text}</span>'
        if link:
            text = f'<a href="{link}" target="_blank">{text}</a>'
        append_fragment(text)
    return JUPYTER_HTML_FORMAT.format(code="".join(fragments))


def _filter_mimebundle(
    data: Dict[str, str], include: Sequence[str], exclude: Sequence[str]
) -> Dict[str, str]:
    if include:
        data = {k: v for (k, v) in data.items() if k in include}
    if exclude:
        data = {k: v for (k, v) in data.items() if k not in exclude}
    return data


def display_html(html: str, text: str) -> None:
    """Display HTML and plain text in Jupyter."""
    jupyter_renderable = JupyterRenderable(html, text)
    try:
        from IPython.display import display as ipython_display

        ipython_display(jupyter_renderable)
    except ModuleNotFoundError:
        pass
