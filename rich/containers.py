from __future__ import annotations

from typing import Iterable, List, Optional, TypeVar, TYPE_CHECKING

from .measure import Measurement

if TYPE_CHECKING:
    from ._types import Console, ConsoleOptions, RenderResult, RenderableType


T = TypeVar("T")


def _renderables_init(
    self, renderables: Optional[Iterable["RenderableType"]] = None
) -> None:
    self._renderables: List["RenderableType"] = (
        list(renderables) if renderables is not None else []
    )


def _renderables_rich_console(
    self, console: "Console", options: "ConsoleOptions"
) -> "RenderResult":
    yield from self._renderables


def _renderables_rich_measure(
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


def _renderables_append(self, renderable: "RenderableType") -> None:
    self._renderables.append(renderable)


def _renderables_iter(self) -> Iterable["RenderableType"]:
    return iter(self._renderables)


Renderables = type(
    "Renderables",
    (),
    {
        "__doc__": "A list subclass which renders its contents to the console.",
        "__init__": _renderables_init,
        "__rich_console__": _renderables_rich_console,
        "__rich_measure__": _renderables_rich_measure,
        "append": _renderables_append,
        "__iter__": _renderables_iter,
    },
)
