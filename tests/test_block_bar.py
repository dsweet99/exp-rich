from rich._measure_fixed_width import measure_fixed_width
from rich.bar import Bar
from rich._console_entry import Console
from rich.measure import Measurement

from .render import render


expected = [
    "\x1b[39;49m     ▐█████████████████████████                   \x1b[0m\n",
    "\x1b[39;49m      ██████████████████████▌                     \x1b[0m\n",
    "\x1b[39;49m                                                  \x1b[0m\n",
]


def test_repr():
    bar = Bar(size=100, begin=11, end=62, width=50)
    assert repr(bar) == "Bar(100, 11, 62)"


def test_render():
    bar = Bar(size=100, begin=11, end=62, width=50)
    bar_render = render(bar)
    assert bar_render == expected[0]
    bar = Bar(size=100, begin=12, end=57, width=50)
    bar_render = render(bar)
    assert bar_render == expected[1]
    # begin after end
    bar = Bar(size=100, begin=60, end=40, width=50)
    bar_render = render(bar)
    assert bar_render == expected[2]


def test_measure_fixed_width_helper():
    console = Console(width=120)
    options = console.options
    assert measure_fixed_width(50, options) == Measurement(50, 50)
    assert measure_fixed_width(None, options) == Measurement(4, 120)


def test_measure():
    console = Console(width=120)
    bar = Bar(size=100, begin=11, end=62)
    measurement = bar.__rich_measure__(console, console.options)
    assert measurement.minimum == 4
    assert measurement.maximum == 120
    bar_fixed = Bar(size=100, begin=11, end=62, width=30)
    assert bar_fixed.__rich_measure__(console, console.options) == Measurement(30, 30)


def test_zero_total():
    # Shouldn't throw zero division error
    bar = Bar(size=0, begin=0, end=0)
    render(bar)


if __name__ == "__main__":
    bar = Bar(size=100, begin=11, end=62, width=50)
    bar_render = render(bar)
    print(repr(bar_render))
    bar = Bar(size=100, begin=12, end=57, width=50)
    bar_render = render(bar)
    print(repr(bar_render))
    bar = Bar(size=100, begin=60, end=40, width=50)
    bar_render = render(bar)
    print(repr(bar_render))
