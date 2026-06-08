"""Stdlib-only AnsiDecoder registry (no rich imports)."""
from __future__ import annotations

from typing import Any, Optional, Type

_ansi_decoder_class: Optional[Type[Any]] = None


def register_ansi_decoder(cls: Type[Any]) -> None:
    global _ansi_decoder_class
    _ansi_decoder_class = cls


def ansi_decoder_class() -> Type[Any]:
    if _ansi_decoder_class is None:
        raise RuntimeError("AnsiDecoder not registered; import rich.ansi first")
    return _ansi_decoder_class
