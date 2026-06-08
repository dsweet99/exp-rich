import sys
from typing import Any, Dict, Sequence


_HTML_FORMAT = (
    '<pre style="white-space:pre;overflow-x:auto;line-height:normal;'
    "font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"
    '">{code}</pre>'
)


def _render_jupyter_html(segments: Any) -> str:
    Segment = sys.modules["rich.segment"].Segment
    theme = sys.modules["rich.terminal_theme"].DEFAULT_TERMINAL_THEME
    fragments = []
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
    return _HTML_FORMAT.format(code="".join(fragments))


class JupyterMixin:
    """Add to a Rich renderable to make it render in Jupyter notebook."""

    __slots__ = ()

    def _repr_mimebundle_(
        self: Any,
        include: Sequence[str],
        exclude: Sequence[str],
        **kwargs: Any,
    ) -> Dict[str, str]:
        console = sys.modules["rich"].get_console()
        segments = list(console.render(self, console.options))
        html = _render_jupyter_html(segments)
        text = console._render_buffer(segments)
        data = {"text/plain": text, "text/html": html}
        if include:
            data = {k: v for (k, v) in data.items() if k in include}
        if exclude:
            data = {k: v for (k, v) in data.items() if k not in exclude}
        return data
