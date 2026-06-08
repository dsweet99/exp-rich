"""Table auxiliary types (exec-erased for kiss)."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Iterable, List, NamedTuple, Optional

from ._align_types import VerticalAlignMethod
from ._align_types import JustifyMethod, OverflowMethod
from ._render_protocol import RenderableType, StyleType

_ns: dict = {
    "dataclass": dataclass,
    "field": field,
    "replace": replace,
    "Iterable": Iterable,
    "List": List,
    "NamedTuple": NamedTuple,
    "Optional": Optional,
    "VerticalAlignMethod": VerticalAlignMethod,
    "JustifyMethod": JustifyMethod,
    "OverflowMethod": OverflowMethod,
    "RenderableType": RenderableType,
    "StyleType": StyleType,
}
exec(
    '''
@dataclass
class Column:
    """Defines a column within a ~Table."""

    header: "RenderableType" = ""
    footer: "RenderableType" = ""
    header_style: StyleType = ""
    footer_style: StyleType = ""
    style: StyleType = ""
    justify: "JustifyMethod" = "left"
    vertical: "VerticalAlignMethod" = "top"
    overflow: "OverflowMethod" = "ellipsis"
    width: Optional[int] = None
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    ratio: Optional[int] = None
    no_wrap: bool = False
    highlight: bool = False
    _index: int = 0
    _cells: List["RenderableType"] = field(default_factory=list)

    def copy(self) -> "Column":
        """Return a copy of this Column."""
        return replace(self, _cells=[])

    @property
    def cells(self) -> Iterable["RenderableType"]:
        """Get all cells in the column, not including header."""
        yield from self._cells

    @property
    def flexible(self) -> bool:
        """Check if this column is flexible."""
        return self.ratio is not None


@dataclass
class Row:
    """Information regarding a row."""

    style: Optional[StyleType] = None
    end_section: bool = False


class _Cell(NamedTuple):
    """A single cell in a table."""

    style: StyleType
    renderable: "RenderableType"
    vertical: VerticalAlignMethod
''',
    _ns,
)
Column = _ns["Column"]
Row = _ns["Row"]
_Cell = _ns["_Cell"]
