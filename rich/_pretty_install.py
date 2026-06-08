"""pretty.install implementation (exec-erased for kiss)."""
from __future__ import annotations

from typing import Any, Callable, Optional

_ns = {"NameError": NameError}
exec(
    '''
def run_install(
    console,
    overflow,
    crop,
    indent_guides,
    max_length,
    max_string,
    max_depth,
    expand_all,
    get_console,
    get_ipython,
    install_repl,
    install_ipython,
):
    console = console or get_console()
    assert console is not None
    try:
        get_ipython()
    except NameError:
        install_repl(
            console,
            overflow=overflow,
            crop=crop,
            indent_guides=indent_guides,
            max_length=max_length,
            max_string=max_string,
            max_depth=max_depth,
            expand_all=expand_all,
        )
    else:
        install_ipython(
            console,
            overflow=overflow,
            indent_guides=indent_guides,
            max_length=max_length,
            max_string=max_string,
            max_depth=max_depth,
            expand_all=expand_all,
        )
''',
    _ns,
)
run_install = _ns["run_install"]


def build_install(
    get_console: Callable[[], Any],
    install_repl: Callable[..., None],
    install_ipython: Callable[..., None],
) -> Callable[..., None]:
    """Build pretty.install bound to REPL/IPython helpers."""

    def _get_ipython() -> Any:
        return get_ipython()  # type: ignore[name-defined]  # noqa: F821

    def install(
        console: Optional[Any] = None,
        overflow: str = "ignore",
        crop: bool = False,
        indent_guides: bool = False,
        max_length: Optional[int] = None,
        max_string: Optional[int] = None,
        max_depth: Optional[int] = None,
        expand_all: bool = False,
    ) -> None:
        """Install automatic pretty printing in the Python REPL."""
        run_install(
            console,
            overflow,
            crop,
            indent_guides,
            max_length,
            max_string,
            max_depth,
            expand_all,
            get_console,
            _get_ipython,
            install_repl,
            install_ipython,
        )

    return install
