"""Stdlib-only deferred module attribute access (no rich imports)."""
from __future__ import annotations

from typing import Any


class DeferredModule:
    """Resolve module attributes on first access via importlib."""

    def __init__(self, module_name: str, package: str | None) -> None:
        self._module_name = module_name
        self._package = package
        self._module: Any = None

    def _get(self) -> Any:
        if self._module is None:
            import importlib

            self._module = importlib.import_module(self._module_name, self._package)
        return self._module

    def __getattr__(self, name: str) -> Any:
        return getattr(self._get(), name)
