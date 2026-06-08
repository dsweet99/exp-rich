FIXTURES_MODULE = __name__


def _inspect_error_str(self) -> str:
    return "INSPECT ERROR"


InspectError = type(
    "InspectError", (Exception,), {"__str__": _inspect_error_str}
)


def _foo_init(self, foo: int) -> None:
    """constructor docs."""
    self.foo = foo


def _foo_broken(self):
    raise InspectError()


def _foo_method(self, a, b) -> str:
    """Multi line

    docs.
    """
    return "test"


def _foo_dir(self):
    return ["__init__", "broken", "method"]


Foo = type(
    "Foo",
    (),
    {
        "__doc__": "Foo test\n\nSecond line",
        "__init__": _foo_init,
        "broken": property(_foo_broken),
        "method": _foo_method,
        "__dir__": _foo_dir,
    },
)
FooSubclass = type("FooSubclass", (Foo,), {})

NotCallable = type(
    "NotCallable",
    (),
    {"__call__": 5, "__repr__": lambda self: "NotCallable()"},
)
BrokenCallFoo = type("BrokenCallFoo", (), {"foo": NotCallable()})


def _broken_class(self):
    raise AttributeError


SwigThing = type("Thing", (), {"__class__": property(_broken_class)})

ModuleThing = type("Thing", (), {"__doc__": "Docstring"})


def make_something_with_doc(doc: str):
    Thing = type("Thing", (), {"__doc__": doc})
    Something = type("Something", (), {"Thing": Thing})
    return Something
