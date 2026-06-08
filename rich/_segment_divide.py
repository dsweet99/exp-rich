"""Segment division helpers."""

from __future__ import annotations

from typing import Iterable, List, Tuple

from .cells import cached_cell_len


def _divide_advance_cut(segments_clear, iter_cuts, new_pos: int) -> Tuple[int, int, bool]:
    segments_clear()
    cut = next(iter_cuts, -1)
    return new_pos, cut, cut == -1


def _divide_emit_cut(add_segment, segment, segments_copy, segments_clear, iter_cuts, end_pos):
    add_segment(segment)
    portion = segments_copy()
    pos, cut, done = _divide_advance_cut(segments_clear, iter_cuts, end_pos)
    return portion, pos, cut, done


def _divide_emit_split(before, segment, add_segment, segments_copy, segments_clear, iter_cuts, cut):
    add_segment(before)
    portion = segments_copy()
    pos, cut, done = _divide_advance_cut(segments_clear, iter_cuts, cut)
    return portion, segment, pos, cut, done


def _divide_tail_if_done(done: bool, split_segments, segments_copy) -> Iterable[List]:
    if done and split_segments:
        yield segments_copy()


def _divide_segment_text(
    segment,
    pos: int,
    cut: int,
    iter_cuts,
    add_segment,
    segments_copy,
    segments_clear,
    split_segments,
    _cell_len,
) -> Iterable[List]:
    text, _style, control = segment
    while text:
        end_pos = pos if control else pos + _cell_len(text)
        if end_pos < cut:
            add_segment(segment)
            return end_pos, cut, False
        if end_pos == cut:
            portion, pos, cut, done = _divide_emit_cut(
                add_segment, segment, segments_copy, segments_clear, iter_cuts, end_pos
            )
            yield portion
            yield from _divide_tail_if_done(done, split_segments, segments_copy)
            return pos, cut, done
        before, segment = segment.split_cells(cut - pos)
        text, _style, control = segment
        portion, segment, pos, cut, done = _divide_emit_split(
            before, segment, add_segment, segments_copy, segments_clear, iter_cuts, cut
        )
        yield portion
        yield from _divide_tail_if_done(done, split_segments, segments_copy)
        if done:
            return pos, cut, True
    return pos, cut, False


def _divide_process_segments(
    segments,
    cut: int,
    iter_cuts,
    add_segment,
    segments_copy,
    segments_clear,
    split_segments,
    _cell_len,
) -> Iterable[List]:
    pos = 0
    for segment in segments:
        pos, cut, done = yield from _divide_segment_text(
            segment, pos, cut, iter_cuts, add_segment,
            segments_copy, segments_clear, split_segments, _cell_len,
        )
        if done:
            return
    yield segments_copy()


def divide_segments_at_cuts(segments: Iterable, cuts: Iterable[int]) -> Iterable[List]:
    split_segments: List = []
    add_segment = split_segments.append
    iter_cuts = iter(cuts)
    while True:
        cut = next(iter_cuts, -1)
        if cut == -1:
            return
        if cut != 0:
            break
        yield []
    segments_clear = split_segments.clear
    segments_copy = split_segments.copy
    yield from _divide_process_segments(
        segments,
        cut,
        iter_cuts,
        add_segment,
        segments_copy,
        segments_clear,
        split_segments,
        cached_cell_len,
    )
