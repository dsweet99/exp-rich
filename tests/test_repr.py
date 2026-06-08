from typing import Optional

import pytest

import rich.repr
from rich.console import Console

from inspect import Parameter


def _foo_init(self, foo: str, bar: Optional[int] = None, egg: int = 1):
    self.foo = foo
    self.bar = bar
    self.egg = egg


def _foo_rich_repr(self):
    yield self.foo
    yield None, self.foo,
    yield "bar", self.bar, None
    yield "egg", self.egg


Foo = rich.repr.auto(
    type(
        "Foo",
        (),
        {"__init__": _foo_init, "__rich_repr__": _foo_rich_repr},
    )
)


def _egg_init(self, foo: str, bar: Optional[int] = None, egg: int = 1):
    self.foo = foo
    self.bar = bar
    self.egg = egg


Egg = rich.repr.auto(type("Egg", (), {"__init__": _egg_init}))


def _broken_egg_init(self, foo: str, *, bar: Optional[int] = None, egg: int = 1):
    self.foo = foo
    self.fubar = bar
    self.egg = egg


BrokenEgg = rich.repr.auto(type("BrokenEgg", (), {"__init__": _broken_egg_init}))


def _angular_egg_init(self, foo: str, *, bar: Optional[int] = None, egg: int = 1):
    self.foo = foo
    self.bar = bar
    self.egg = egg


AngularEgg = rich.repr.auto(angular=True)(
    type("AngularEgg", (), {"__init__": _angular_egg_init})
)


def _bar_rich_repr(self):
    yield (self.foo,)
    yield None, self.foo,
    yield "bar", self.bar, None
    yield "egg", self.egg


Bar = rich.repr.auto(
    type(
        "Bar",
        (Foo,),
        {"__rich_repr__": _bar_rich_repr},
    )
)
Bar.__rich_repr__.angular = True  # type: ignore[attr-defined]


def _stupid_init(self, a):
    self.a = a


def _stupid_eq(self, other) -> bool:
    if other is Parameter.empty:
        return True
    try:
        return self.a == other.a
    except Exception:
        return False


def _stupid_ne(self, other: object) -> bool:
    return not self.__eq__(other)


StupidClass = type(
    "StupidClass",
    (),
    {"__init__": _stupid_init, "__eq__": _stupid_eq, "__ne__": _stupid_ne},
)

NotStupid = type("NotStupid", (), {})


def _bird_init(
    self, name, eats, fly=True, another=StupidClass(2), extinct=NotStupid()
):
    self.name = name
    self.eats = eats
    self.fly = fly
    self.another = another
    self.extinct = extinct


Bird = rich.repr.auto(type("Bird", (), {"__init__": _bird_init}))


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
