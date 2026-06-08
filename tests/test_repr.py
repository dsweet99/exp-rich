import pytest

import rich.repr
from rich._console_entry import Console

from tests._repr_fixtures import (
    AngularEgg,
    Bar,
    Bird,
    BrokenEgg,
    Egg,
    Foo,
    NotStupid,
    StupidClass,
)


def test_rich_repr() -> None:
    assert (repr(Foo("hello"))) == "Foo('hello', 'hello', egg=1)"
    assert (repr(Foo("hello", bar=3))) == "Foo('hello', 'hello', bar=3, egg=1)"


def test_rich_repr_positional_only() -> None:
    _locals = locals().copy()
    exec(
        """\
@rich.repr.auto
class PosOnly:
    def __init__(self, foo, /):
        self.foo = 1
    """,
        globals(),
        _locals,
    )
    p = _locals["PosOnly"](1)
    assert repr(p) == "PosOnly(1)"


def test_rich_angular() -> None:
    assert (repr(Bar("hello"))) == "<Bar 'hello' 'hello' egg=1>"
    assert (repr(Bar("hello", bar=3))) == "<Bar 'hello' 'hello' bar=3 egg=1>"


def test_rich_repr_auto() -> None:
    assert repr(Egg("hello", egg=2)) == "Egg('hello', egg=2)"
    stupid_class = StupidClass(9)
    not_stupid = NotStupid()
    assert (
        repr(Bird("penguin", ["fish"], another=stupid_class, extinct=not_stupid))
        == f"Bird('penguin', ['fish'], another={repr(stupid_class)}, extinct={repr(not_stupid)})"
    )


def test_rich_repr_auto_angular() -> None:
    assert repr(AngularEgg("hello", egg=2)) == "<AngularEgg 'hello' egg=2>"


def test_broken_egg() -> None:
    with pytest.raises(rich.repr.ReprError):
        repr(BrokenEgg("foo"))


def test_rich_pretty() -> None:
    console = Console()
    with console.capture() as capture:
        console.print(Foo("hello", bar=3))
    result = capture.get()
    expected = "Foo('hello', 'hello', bar=3, egg=1)\n"
    assert result == expected


def test_rich_pretty_angular() -> None:
    console = Console()
    with console.capture() as capture:
        console.print(Bar("hello", bar=3))
    result = capture.get()
    expected = "<Bar 'hello' 'hello' bar=3 egg=1>\n"
    assert result == expected
