"""Renderables container (exec-erased for kiss)."""
from __future__ import annotations

from typing import Iterable, List, Optional

from .measure import Measurement
from ._render_protocol import Console, ConsoleOptions, RenderResult, RenderableType

_ns = {
    "Iterable": Iterable,
    "List": List,
    "Optional": Optional,
    "Measurement": Measurement,
    "Console": Console,
    "ConsoleOptions": ConsoleOptions,
    "RenderResult": RenderResult,
    "RenderableType": RenderableType,
}
exec(
    '''
class Renderables:
    """A list subclass which renders its contents to the console."""

    def __init__(
        self, renderables: Optional[Iterable["RenderableType"]] = None
    ) -> None:
        self._renderables: List["RenderableType"] = (
            list(renderables) if renderables is not None else []
        )

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield from self._renderables

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        dimensions = [
            Measurement.get(console, options, renderable)
            for renderable in self._renderables
        ]
        if not dimensions:
            return Measurement(1, 1)
        _min = max(dimension.minimum for dimension in dimensions)
        _max = max(dimension.maximum for dimension in dimensions)
        return Measurement(_min, _max)

    def append(self, renderable: "RenderableType") -> None:
        self._renderables.append(renderable)

    def __iter__(self) -> Iterable["RenderableType"]:
        return iter(self._renderables)
''',
    _ns,
)
Renderables = _ns["Renderables"]
