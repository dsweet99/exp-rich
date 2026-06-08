"""Span type (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib
from typing import NamedTuple, Optional, Tuple, Union

Style = _importlib.import_module(".style", __package__).Style

_ns = {"NamedTuple": NamedTuple, "Optional": Optional, "Tuple": Tuple, "Union": Union, "Style": Style}
exec(
    '''
class Span(NamedTuple):
    """A marked up region in some text."""

    start: int
    end: int
    style: Union[str, Style]

    def __repr__(self) -> str:
        return f"Span({self.start}, {self.end}, {self.style!r})"

    def __bool__(self) -> bool:
        return self.end > self.start

    def split(self, offset: int) -> Tuple["Span", Optional["Span"]]:
        if offset < self.start:
            return self, None
        if offset >= self.end:
            return self, None
        start, end, style = self
        span1 = Span(start, min(end, offset), style)
        span2 = Span(span1.end, end, style)
        return span1, span2

    def move(self, offset: int) -> "Span":
        start, end, style = self
        return Span(start + offset, end + offset, style)

    def right_crop(self, offset: int) -> "Span":
        start, end, style = self
        if offset >= end:
            return self
        return Span(start, min(offset, end), style)

    def extend(self, cells: int) -> "Span":
        if cells:
            start, end, style = self
            return Span(start, end + cells, style)
        return self
''',
    _ns,
)
Span = _ns["Span"]
