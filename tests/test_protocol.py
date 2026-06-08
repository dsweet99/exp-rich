import io

from rich.abc import RichRenderable
from rich._console_entry import Console
from rich.panel import Panel
from rich.protocol import is_renderable, rich_cast
from rich.text import Text

Foo = type("Foo", (), {"__rich__": lambda self: Text("Foo")})
Fake = type(
    "Fake",
    (),
    {"__getattr__": lambda self, name: 12, "__repr__": lambda self: "Fake()"},
)


def test_rich_cast():
    foo = Foo()
    assert is_renderable(foo)
    assert rich_cast("hello") == "hello"
    console = Console(file=io.StringIO())
    console.print(foo)
    assert console.file.getvalue() == "Foo\n"


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
    _locals: dict = {"Foo": Foo, "Text": Text}
    exec(
        """
class B:
    def __rich__(self) -> Foo:
        return Foo()

class A:
    def __rich__(self) -> B:
        return B()
""",
        _locals,
    )
    A = _locals["A"]
    console = Console(file=io.StringIO())
    console.print(A())
    assert console.file.getvalue() == "Foo\n"


def test_cast_recursive():
    _locals = {}
    exec(
        """
class B:
    def __rich__(self) -> "A":
        return A()

    def __repr__(self) -> str:
        return "<B>"

class A:
    def __rich__(self) -> B:
        return B()

    def __repr__(self) -> str:
        return "<A>"
""",
        _locals,
    )
    A = _locals["A"]
    console = Console(file=io.StringIO())
    console.print(A())
    assert console.file.getvalue() == "<B>\n"
