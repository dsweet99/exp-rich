from typing import Iterable, Iterator, List, Tuple, Union

from .cells import cached_cell_len


def _divide_skip_zero_cuts(
    cuts: Iterable[int],
) -> Iterable[Union[int, List]]:
    iter_cuts = iter(cuts)
    while True:
        cut = next(iter_cuts, -1)
        if cut == -1:
            return
        if cut == 0:
            yield []
            continue
        yield cut
        yield from iter_cuts
        return


def _divide_end_pos(segment, pos: int, _cell_len) -> int:
    text, _style, control = segment
    return pos if control else pos + _cell_len(text)


def _divide_yield_remainder(split_segments: List, segments_copy) -> Iterable[List]:
    if split_segments:
        yield segments_copy()


def _divide_take_next_cut(
    cut_iter: Iterator, split_segments: List, segments_copy
) -> Tuple[int, bool]:
    cut = next(cut_iter, -1)
    if cut != -1:
        return cut, False
    return cut, True


def _divide_emit_and_advance(
    cut_iter: Iterator,
    split_segments: List,
    segments_copy,
    segments_clear,
) -> Iterable:
    yield segments_copy()
    segments_clear()
    cut, finished = _divide_take_next_cut(cut_iter, split_segments, segments_copy)
    if finished:
        yield from _divide_yield_remainder(split_segments, segments_copy)
    return cut, finished


def _divide_drain_processor(processor) -> Iterable:
    while True:
        try:
            yield next(processor)
        except StopIteration as stop:
            return stop.value


def _divide_process_segment(
    segment,
    cut: int,
    cut_iter: Iterator,
    pos: int,
    split_segments: List,
    add_segment,
    segments_copy,
    segments_clear,
    _cell_len,
) -> Iterable:
    """Process one segment against current cuts."""
    text, _style, control = segment
    while text:
        end_pos = _divide_end_pos(segment, pos, _cell_len)
        if end_pos < cut:
            add_segment(segment)
            return cut, end_pos, False

        if end_pos == cut:
            add_segment(segment)
            cut, finished = yield from _divide_emit_and_advance(
                cut_iter, split_segments, segments_copy, segments_clear
            )
            return cut, end_pos, finished

        before, segment = segment.split_cells(cut - pos)
        text, _style, control = segment
        add_segment(before)
        pos = cut
        cut, finished = yield from _divide_emit_and_advance(
            cut_iter, split_segments, segments_copy, segments_clear
        )
        if finished:
            return cut, pos, True

    return cut, pos, False


def divide_segments(
    cls: type, segments: Iterable, cuts: Iterable[int]
) -> Iterable[List]:
    """Divide segments at cell positions."""
    cut_iter = _divide_skip_zero_cuts(cuts)
    try:
        cut = next(cut_iter)
    except StopIteration:
        return
    if not isinstance(cut, int):
        return

    split_segments: List = []
    add_segment = split_segments.append
    segments_clear = split_segments.clear
    segments_copy = split_segments.copy
    _cell_len = cached_cell_len
    pos = 0

    for segment in segments:
        cut, pos, done = yield from _divide_drain_processor(
            _divide_process_segment(
                segment,
                cut,
                cut_iter,
                pos,
                split_segments,
                add_segment,
                segments_copy,
                segments_clear,
                _cell_len,
            )
        )
        if done:
            return

    yield segments_copy()
