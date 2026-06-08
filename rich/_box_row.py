"""Box row edge helpers (extracted for kiss complexity)."""
from __future__ import annotations

from typing import Iterable, Literal, Tuple

from ._loop import loop_last


def box_row_edges(
    box: object,
    level: Literal["head", "row", "foot", "mid"],
) -> Tuple[str, str, str, str]:
    """Return (left, horizontal, cross, right) characters for a box row level."""
    if level == "head":
        return (
            box.head_row_left,
            box.head_row_horizontal,
            box.head_row_cross,
            box.head_row_right,
        )
    if level == "row":
        return (
            box.row_left,
            box.row_horizontal,
            box.row_cross,
            box.row_right,
        )
    if level == "mid":
        return (box.mid_left, " ", box.mid_vertical, box.mid_right)
    if level == "foot":
        return (
            box.foot_row_left,
            box.foot_row_horizontal,
            box.foot_row_cross,
            box.foot_row_right,
        )
    raise ValueError("level must be 'head', 'row' or 'foot'")


def build_box_row(
    left: str,
    horizontal: str,
    cross: str,
    right: str,
    widths: Iterable[int],
    *,
    edge: bool,
) -> str:
    """Assemble a horizontal box row from edge characters and column widths."""
    parts: list[str] = []
    append = parts.append
    if edge:
        append(left)
    for last, width in loop_last(widths):
        append(horizontal * width)
        if not last:
            append(cross)
    if edge:
        append(right)
    return "".join(parts)
