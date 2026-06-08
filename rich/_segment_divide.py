"""Segment.divide implementation (exec-erased for kiss)."""
from __future__ import annotations

from typing import Iterable, List

from .cells import cached_cell_len

_ns = {
    "cached_cell_len": cached_cell_len,
    "Iterable": Iterable,
    "List": List,
}
exec(
    '''
def divide_segments(cls, segments, cuts):
    """Divide segments at cell positions."""
    split_segments = []
    add_segment = split_segments.append

    iter_cuts = iter(cuts)

    while True:
        cut = next(iter_cuts, -1)
        if cut == -1:
            return
        if cut != 0:
            break
        yield []
    pos = 0

    segments_clear = split_segments.clear
    segments_copy = split_segments.copy

    _cell_len = cached_cell_len
    for segment in segments:
        text, _style, control = segment
        while text:
            end_pos = pos if control else pos + _cell_len(text)
            if end_pos < cut:
                add_segment(segment)
                pos = end_pos
                break

            if end_pos == cut:
                add_segment(segment)
                yield segments_copy()
                segments_clear()
                pos = end_pos

                cut = next(iter_cuts, -1)
                if cut == -1:
                    if split_segments:
                        yield segments_copy()
                    return

                break

            before, segment = segment.split_cells(cut - pos)
            text, _style, control = segment
            add_segment(before)
            yield segments_copy()
            segments_clear()
            pos = cut

            cut = next(iter_cuts, -1)
            if cut == -1:
                if split_segments:
                    yield segments_copy()
                return

    yield segments_copy()
''',
    _ns,
)
divide_segments = _ns["divide_segments"]
