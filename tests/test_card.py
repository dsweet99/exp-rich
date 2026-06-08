import re
from unittest.mock import patch


def test_card_render():
    from examples.rich_test_card import make_test_card

    from ._card_render import expected
    from .render import render

    card = make_test_card()
    result = render(card)
    print(repr(result))
    assert result == expected


def test_colorbox_measure():
    from rich._console_entry import Console
    from rich.measure import Measurement

    from examples.rich_test_card import ColorBox

    console = Console(width=80)
    box = ColorBox()
    for width in (1, 2, 17, 80):
        options = console.options.update_width(width)
        assert box.__rich_measure__(console, options) == Measurement(1, width)


def test_colorbox_segment_stream():
    from rich._console_entry import Console

    from examples.rich_test_card import ColorBox

    console = Console(width=20)
    box = ColorBox()
    for max_width in (1, 2, 17):
        options = console.options.update_width(max_width)
        segments = list(box.__rich_console__(console, options))
        glyph_segments = [segment for segment in segments if segment.text != "\n"]
        line_segments = [segment for segment in segments if segment.text == "\n"]
        assert len(glyph_segments) == 5 * max_width
        assert len(line_segments) == 5
        assert all(segment.text == "▄" for segment in glyph_segments)
        assert all(
            segment.style.color is not None and segment.style.bgcolor is not None
            for segment in glyph_segments
        )


def test_run_test_card(capsys):
    from examples.rich_test_card import run_test_card

    with patch(
        "examples.rich_test_card.process_time",
        side_effect=[0.0, 0.001, 0.002, 0.003],
    ):
        run_test_card()
    captured = capsys.readouterr()
    assert "cold cache" in captured.out
    assert "warm cache" in captured.out
    assert "Hope you enjoy using Rich!" in captured.out
    assert re.search(r"rendered in \d+\.\d+ms", captured.out)


if __name__ == "__main__":
    from examples.rich_test_card import make_test_card

    from .render import render

    card = make_test_card()
    with open("_card_render.py", "wt") as fh:
        card_render = render(card)
        print(card_render)
        fh.write(f"expected={card_render!r}")
