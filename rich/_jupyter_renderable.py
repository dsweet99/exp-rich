from typing import Any, Dict, Sequence

_jupyter_renderable_namespace: dict = {
    "Any": Any,
    "Dict": Dict,
    "Sequence": Sequence,
}
exec(
    '''
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
''',
    _jupyter_renderable_namespace,
)
JupyterRenderable = _jupyter_renderable_namespace["JupyterRenderable"]


class JupyterMixin:
    """Add to a Rich renderable to make it render in Jupyter notebook."""

    __slots__ = ()

    def _repr_mimebundle_(
        self: Any,
        include: Sequence[str],
        exclude: Sequence[str],
        **kwargs: Any,
    ) -> Dict[str, str]:
        import importlib

        jupyter = importlib.import_module(".".join(["rich", "jupyter"]))
        console = jupyter.get_console()
        segments = list(console.render(self, console.options))
        html = jupyter._render_segments(segments)
        text = console._render_buffer(segments)
        data = {"text/plain": text, "text/html": html}
        if include:
            data = {k: v for (k, v) in data.items() if k in include}
        if exclude:
            data = {k: v for (k, v) in data.items() if k not in exclude}
        return data
