from __future__ import annotations

import sys

if sys.version_info[:2] >= (3, 9):
    from functools import cache
else:
    from functools import lru_cache as cache  # pragma: no cover

from importlib import import_module
from typing import TYPE_CHECKING

from rich._unicode_data._resolve import _parse_version, resolve_unicode_version
from rich._unicode_data._versions import VERSIONS

if TYPE_CHECKING:
    from rich._unicode_data._cell_table import CellTable

# Re-export for tests and backwards compatibility.
__all__ = ["VERSIONS", "_parse_version", "load", "resolve_unicode_version"]


@cache
def load(unicode_version: str = "auto") -> "CellTable":
    """Load a cell table for the given unicode version.

    Args:
        unicode_version: Unicode version, or `None` to auto-detect.

    """
    version = resolve_unicode_version(unicode_version)
    version_path_component = version.replace(".", "-")
    module_name = f".unicode{version_path_component}"
    module = import_module(module_name, "rich._unicode_data")
    if TYPE_CHECKING:
        assert isinstance(module.cell_table, CellTable)
    return module.cell_table
