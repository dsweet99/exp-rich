import re

import pytest


def assert_frame_preambles(rendered_exception: str) -> None:
    frame_blank_line_possible_preambles = (
        "╭─────────────────────────────── Traceback (most recent call last) ────────────────────────────────╮",
        "│" + (" " * 98) + "│",
    )
    for frame_start in re.finditer(
        "^│ .+rich/tests/test_traceback.py:",
        rendered_exception,
        flags=re.MULTILINE,
    ):
        frame_start_index = frame_start.start()
        for preamble in frame_blank_line_possible_preambles:
            preamble_start, preamble_end = (
                frame_start_index - len(preamble) - 1,
                frame_start_index - 1,
            )
            if rendered_exception[preamble_start:preamble_end] == preamble:
                break
        else:
            pytest.fail(
                f"Frame {frame_start[0]} doesn't have the expected preamble"
            )
