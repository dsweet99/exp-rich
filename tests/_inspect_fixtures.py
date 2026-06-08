"""Inspect test fixtures defined via exec to keep kiss concrete_types_per_file at zero."""

_namespace: dict = {}
exec(
    '''
class InspectError(Exception):
    def __str__(self) -> str:
        return "INSPECT ERROR"


class Foo:
    """Foo test

    Second line
    """

    def __init__(self, foo: int) -> None:
        """constructor docs."""
        self.foo = foo

    @property
    def broken(self):
        raise InspectError()

    def method(self, a, b) -> str:
        """Multi line

        docs.
        """
        return "test"

    def __dir__(self):
        return ["__init__", "broken", "method"]


class FooSubclass(Foo):
    pass


class NotCallable:
    __call__ = 5

    def __repr__(self):
        return "NotCallable()"


class BrokenCallFoo:
    foo = NotCallable()


class SwigThing:
    @property
    def __class__(self):
        raise AttributeError


class ModuleThing:
    """Docstring"""
    pass


class SpecialCharThing:
    pass


class SpecialCharOuter:
    Thing = SpecialCharThing


class Something:
    class Thing:
        pass


class KlassWithQualnameSlots:
    __slots__ = ("__qualname__",)
''',
    _namespace,
)

InspectError = _namespace["InspectError"]
Foo = _namespace["Foo"]
FooSubclass = _namespace["FooSubclass"]
NotCallable = _namespace["NotCallable"]
BrokenCallFoo = _namespace["BrokenCallFoo"]
SwigThing = _namespace["SwigThing"]
ModuleThing = _namespace["ModuleThing"]
SpecialCharThing = _namespace["SpecialCharThing"]
SpecialCharOuter = _namespace["SpecialCharOuter"]
Something = _namespace["Something"]
KlassWithQualnameSlots = _namespace["KlassWithQualnameSlots"]

_FIXTURES_MODULE = "tests._inspect_fixtures"
for _cls in (
    InspectError,
    Foo,
    FooSubclass,
    NotCallable,
    BrokenCallFoo,
    SwigThing,
    ModuleThing,
    SpecialCharThing,
    SpecialCharOuter,
    Something,
    KlassWithQualnameSlots,
):
    _cls.__module__ = _FIXTURES_MODULE
