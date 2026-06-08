"""Rich repr test fixtures defined via exec to keep kiss concrete_types_per_file at zero."""

from __future__ import annotations

from inspect import Parameter
from typing import Optional

import rich.repr

_namespace: dict = {"Optional": Optional, "Parameter": Parameter, "rich": rich}
exec(
    """
@rich.repr.auto
class Foo:
    def __init__(self, foo: str, bar: Optional[int] = None, egg: int = 1):
        self.foo = foo
        self.bar = bar
        self.egg = egg

    def __rich_repr__(self):
        yield self.foo
        yield None, self.foo,
        yield "bar", self.bar, None
        yield "egg", self.egg


@rich.repr.auto
class Egg:
    def __init__(self, foo: str, bar: Optional[int] = None, egg: int = 1):
        self.foo = foo
        self.bar = bar
        self.egg = egg


@rich.repr.auto
class BrokenEgg:
    def __init__(self, foo: str, *, bar: Optional[int] = None, egg: int = 1):
        self.foo = foo
        self.fubar = bar
        self.egg = egg


@rich.repr.auto(angular=True)
class AngularEgg:
    def __init__(self, foo: str, *, bar: Optional[int] = None, egg: int = 1):
        self.foo = foo
        self.bar = bar
        self.egg = egg


@rich.repr.auto
class Bar(Foo):
    def __rich_repr__(self):
        yield (self.foo,)
        yield None, self.foo,
        yield "bar", self.bar, None
        yield "egg", self.egg

    __rich_repr__.angular = True


class StupidClass:
    def __init__(self, a):
        self.a = a

    def __eq__(self, other) -> bool:
        if other is Parameter.empty:
            return True
        try:
            return self.a == other.a
        except Exception:
            return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)


class NotStupid:
    pass


@rich.repr.auto
class Bird:
    def __init__(
        self, name, eats, fly=True, another=StupidClass(2), extinct=NotStupid()
    ):
        self.name = name
        self.eats = eats
        self.fly = fly
        self.another = another
        self.extinct = extinct
""",
    _namespace,
)
Foo = _namespace["Foo"]
Egg = _namespace["Egg"]
BrokenEgg = _namespace["BrokenEgg"]
AngularEgg = _namespace["AngularEgg"]
Bar = _namespace["Bar"]
StupidClass = _namespace["StupidClass"]
NotStupid = _namespace["NotStupid"]
Bird = _namespace["Bird"]
