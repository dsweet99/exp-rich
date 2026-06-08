"""Traceback.__init__ helpers (extracted for kiss)."""
from __future__ import annotations

import os
import sys
from types import ModuleType
from typing import Iterable, Optional, Sequence, Union


def resolve_trace_or_raise(
    trace: Optional[object],
    *,
    extract: object,
    show_locals: bool,
) -> object:
    if trace is not None:
        return trace
    exc_type, exc_value, traceback = sys.exc_info()
    if exc_type is None or exc_value is None or traceback is None:
        raise ValueError(
            "Value for 'trace' required if not called in except: block"
        )
    return extract(exc_type, exc_value, traceback, show_locals=show_locals)


def normalize_suppress_paths(
    suppress: Iterable[Union[str, ModuleType]],
) -> Sequence[str]:
    paths: list[str] = []
    for suppress_entity in suppress:
        if not isinstance(suppress_entity, str):
            assert (
                suppress_entity.__file__ is not None
            ), f"{suppress_entity!r} must be a module with '__file__' attribute"
            path = os.path.dirname(suppress_entity.__file__)
        else:
            path = suppress_entity
        paths.append(os.path.normpath(os.path.abspath(path)))
    return paths
