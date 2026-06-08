"""IPython pretty-print formatter (extracted for kiss)."""
from __future__ import annotations

from typing import Any, Callable, Optional


def register_ipython_formatter(
    ip: Any,
    display_hook: Callable[..., Any],
    *,
    console: Any,
    overflow: str,
    indent_guides: bool,
    max_length: Optional[int],
    max_string: Optional[int],
    max_depth: Optional[int],
    expand_all: bool,
) -> None:
    """Replace plain text formatter with Rich formatter in IPython."""
    from IPython.core.formatters import BaseFormatter

    class RichFormatter(BaseFormatter):  # type: ignore[misc]
        pprint: bool = True

        def __call__(self, value: Any) -> Any:
            if self.pprint:
                return display_hook(
                    value,
                    console=console,
                    overflow=overflow,
                    indent_guides=indent_guides,
                    max_length=max_length,
                    max_string=max_string,
                    max_depth=max_depth,
                    expand_all=expand_all,
                )
            return repr(value)

    ip.display_formatter.formatters["text/plain"] = RichFormatter()
