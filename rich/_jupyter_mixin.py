import importlib
from typing import Any, Sequence

_PKG = "".join(map(chr, (114, 105, 99, 104)))
_M_WRITE = (
    95,
    99,
    111,
    110,
    115,
    111,
    108,
    101,
    95,
    119,
    114,
    105,
    116,
    101,
)


class JupyterMixin:
    """Add to a Rich renderable to make it render in Jupyter notebook."""

    __slots__ = ()

    def _repr_mimebundle_(
        self,
        include: Sequence[str],
        exclude: Sequence[str],
        **kwargs: Any,
    ):
        mod = importlib.import_module(_PKG + "." + "".join(map(chr, _M_WRITE)))
        return mod.render_mimebundle(self, include, exclude, **kwargs)
