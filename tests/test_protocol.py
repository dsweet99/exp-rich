import io

from rich.abc import RichRenderable
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

Foo = type("Foo", (), {"__rich__": lambda self: Text("Foo")})


def test_rich_cast():
    foo = Foo()
    console = Console(file=io.StringIO())
    console.print(foo)
    assert console.file.getvalue() == "Foo\n"


Fake = type(
    "Fake",
    (),
    {
        "__getattr__": lambda self, name: 12,
        "__repr__": lambda self: "Fake()",
    },
)


def test_rich_cast_fake():
    fake = Fake()
    console = Console(file=io.StringIO())
    console.print(fake)
    assert console.file.getvalue() == "Fake()\n"


def test_rich_cast_container():
    foo = Foo()
    console = Console(file=io.StringIO(), legacy_windows=False)
    console.print(Panel.fit(foo, padding=0))
    assert console.file.getvalue() == "╭───╮\n│Foo│\n╰───╯\n"


def test_abc():
    foo = Foo()
    assert isinstance(foo, RichRenderable)
    assert isinstance(Text("hello"), RichRenderable)
    assert isinstance(Panel("hello"), RichRenderable)
    assert not isinstance(foo, str)
    assert not isinstance("foo", RichRenderable)
    assert not isinstance([], RichRenderable)


def test_cast_deep():
    B = type("B", (), {"__rich__": lambda self: Foo()})
    A = type("A", (), {"__rich__": lambda self: B()})

    console = Console(file=io.StringIO())
    console.print(A())
    assert console.file.getvalue() == "Foo\n"


def test_cast_recursive():
    def _b_rich(self):
        return A()

    def _b_repr(self):
        return "<B>"

    def _a_rich(self):
        return B()

    def _a_repr(self):
        return "<A>"

    B = type("B", (), {"__rich__": _b_rich, "__repr__": _b_repr})
    A = type("A", (), {"__rich__": _a_rich, "__repr__": _a_repr})

    console = Console(file=io.StringIO())
    console.print(A())
    assert console.file.getvalue() == "<B>\n"
