import builtins
import collections
import io
import sys
from array import array
from collections import UserDict, defaultdict, deque
from dataclasses import field, make_dataclass
from typing import Any, List, NamedTuple

import attr
import pytest

from rich._console_entry import Console
from rich.measure import Measurement
from rich.pretty import Node, Pretty, _Line, _ipy_display_hook, install, pprint, pretty_repr
from rich.text import Text

install
Node.iter_tokens
Node.check_length
_Line.expandable
_Line.check_length

skip_py38 = pytest.mark.skipif(
    sys.version_info.minor == 8 and sys.version_info.major == 3,
    reason="rendered differently on py3.8",
)
skip_py39 = pytest.mark.skipif(
    sys.version_info.minor == 9 and sys.version_info.major == 3,
    reason="rendered differently on py3.9",
)
skip_py310 = pytest.mark.skipif(
    sys.version_info.minor == 10 and sys.version_info.major == 3,
    reason="rendered differently on py3.10",
)
skip_py311 = pytest.mark.skipif(
    sys.version_info.minor == 11 and sys.version_info.major == 3,
    reason="rendered differently on py3.11",
)
skip_py312 = pytest.mark.skipif(
    sys.version_info.minor == 12 and sys.version_info.major == 3,
    reason="rendered differently on py3.12",
)
skip_py313 = pytest.mark.skipif(
    sys.version_info.minor == 13 and sys.version_info.major == 3,
    reason="rendered differently on py3.13",
)
skip_py314 = pytest.mark.skipif(
    sys.version_info.minor == 14 and sys.version_info.major == 3,
    reason="rendered differently on py3.14",
)


def test_node_iter_tokens_and_check_length() -> None:
    child = Node(value_repr="1", last=True)
    parent = Node(open_brace="{", close_brace="}", children=[child])
    assert list(parent.iter_tokens()) == ["{", "1", "}"]
    assert parent.check_length(0, 80)
    assert not parent.check_length(0, 2)


def test_line_expandable_and_check_length() -> None:
    child = Node(value_repr="x" * 20, last=True)
    node = Node(open_brace="{", close_brace="}", children=[child])
    line = _Line(node=node, text="")
    assert line.expandable
    assert line.check_length(80)
    assert not line.check_length(5)


def test_repl_display_hook() -> None:
    console = Console(file=io.StringIO())
    from rich.pretty import _repl_display_hook

    _repl_display_hook(
        {"a": 1},
        console=console,
        overflow="ignore",
        crop=False,
        indent_guides=False,
        max_length=None,
        max_string=None,
        max_depth=None,
        expand_all=False,
    )
    assert console.file.getvalue()


def test_install() -> None:
    console = Console(file=io.StringIO())
    dh = sys.displayhook
    try:
        install(console)
        sys.displayhook("foo")
        assert console.file.getvalue() == "'foo'\n"
        assert sys.displayhook is not dh
    finally:
        sys.displayhook = dh


def test_install_max_depth() -> None:
    console = Console(file=io.StringIO())
    dh = sys.displayhook
    try:
        install(console, max_depth=1)
        sys.displayhook({"foo": {"bar": True}})
        assert console.file.getvalue() == "{'foo': {...}}\n"
        assert sys.displayhook is not dh
    finally:
        sys.displayhook = dh


def test_install_ipython_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import MagicMock

    console = Console(file=io.StringIO())
    ip = MagicMock()
    formatters: dict = {}
    ip.display_formatter.formatters = formatters
    monkeypatch.setattr(builtins, "get_ipython", lambda: ip, raising=False)
    try:
        install(console, max_depth=1, crop=True)
        assert "text/plain" in formatters
        assert callable(formatters["text/plain"])
    finally:
        monkeypatch.delattr(builtins, "get_ipython", raising=False)


def test_ipy_display_hook__repr_html() -> None:
    console = Console(file=io.StringIO(), force_jupyter=True)

    Thing = type("Thing", (), {"_repr_html_": lambda self: "hello"})

    console.begin_capture()
    _ipy_display_hook(Thing(), console=console)

    # Rendering delegated to notebook because _repr_html_ method exists
    assert console.end_capture() == ""


def test_ipy_display_hook__multiple_special_reprs() -> None:
    """
    The case where there are multiple IPython special _repr_*_
    methods on the object, and one of them returns None but another
    one does not.
    """
    console = Console(file=io.StringIO(), force_jupyter=True)

    Thing = type(
        "Thing",
        (),
        {
            "__repr__": lambda self: "A Thing",
            "_repr_latex_": lambda self: None,
            "_repr_html_": lambda self: "hello",
        },
    )

    result = _ipy_display_hook(Thing(), console=console)
    assert result == "A Thing"


def test_ipy_display_hook__no_special_repr_methods() -> None:
    console = Console(file=io.StringIO(), force_jupyter=True)

    Thing = type("Thing", (), {"__repr__": lambda self: "hello"})

    result = _ipy_display_hook(Thing(), console=console)
    # should be repr as-is
    assert result == "hello"


def test_ipy_display_hook__special_repr_raises_exception() -> None:
    """
    When an IPython special repr method raises an exception,
    we treat it as if it doesn't exist and look for the next.
    """
    console = Console(file=io.StringIO(), force_jupyter=True)

    def _repr_markdown_raises(_self):
        raise Exception()

    Thing = type(
        "Thing",
        (),
        {
            "_repr_markdown_": _repr_markdown_raises,
            "_repr_latex_": lambda self: None,
            "_repr_html_": lambda self: "hello",
            "__repr__": lambda self: "therepr",
        },
    )

    result = _ipy_display_hook(Thing(), console=console)
    assert result == "therepr"


def test_ipy_display_hook__console_renderables_on_newline() -> None:
    console = Console(file=io.StringIO(), force_jupyter=True)
    console.begin_capture()
    result = _ipy_display_hook(Text("hello"), console=console)
    assert result == "\nhello"


def test_pretty() -> None:
    test = {
        "foo": [1, 2, 3, (4, 5, {6}, 7, 8, {9}), {}],
        "bar": {"egg": "baz", "words": ["Hello World"] * 10},
        False: "foo",
        True: "",
        "text": ("Hello World", "foo bar baz egg"),
    }

    result = pretty_repr(test, max_width=80)
    print(result)
    expected = "{\n    'foo': [1, 2, 3, (4, 5, {6}, 7, 8, {9}), {}],\n    'bar': {\n        'egg': 'baz',\n        'words': [\n            'Hello World',\n            'Hello World',\n            'Hello World',\n            'Hello World',\n            'Hello World',\n            'Hello World',\n            'Hello World',\n            'Hello World',\n            'Hello World',\n            'Hello World'\n        ]\n    },\n    False: 'foo',\n    True: '',\n    'text': ('Hello World', 'foo bar baz egg')\n}"
    print(expected)
    assert result == expected


ExampleDataclass = make_dataclass(
    "ExampleDataclass",
    [
        ("foo", int),
        ("bar", str),
        ("ignore", int, field(repr=False, default=0)),
        ("baz", List[str], field(default_factory=list)),
        ("last", int, field(default=1, repr=False)),
    ],
)
Empty = make_dataclass("Empty", [])


StockKeepingUnit = NamedTuple(
    "StockKeepingUnit",
    [
        ("name", str),
        ("description", str),
        ("price", float),
        ("category", str),
        ("reviews", List[str]),
    ],
)


def test_pretty_dataclass() -> None:
    dc = ExampleDataclass(1000, "Hello, World", 999, ["foo", "bar", "baz"])
    result = pretty_repr(dc, max_width=80)
    print(repr(result))
    assert (
        result
        == "ExampleDataclass(foo=1000, bar='Hello, World', baz=['foo', 'bar', 'baz'])"
    )
    result = pretty_repr(dc, max_width=16)
    print(repr(result))
    assert (
        result
        == "ExampleDataclass(\n    foo=1000,\n    bar='Hello, World',\n    baz=[\n        'foo',\n        'bar',\n        'baz'\n    ]\n)"
    )
    dc.bar = dc
    result = pretty_repr(dc, max_width=80)
    print(repr(result))
    assert result == "ExampleDataclass(foo=1000, bar=..., baz=['foo', 'bar', 'baz'])"


def test_empty_dataclass() -> None:
    assert pretty_repr(Empty()) == "Empty()"
    assert pretty_repr([Empty()]) == "[Empty()]"


def test_pretty_namedtuple() -> None:
    console = Console(color_system=None)
    console.begin_capture()

    example_namedtuple = StockKeepingUnit(
        "Sparkling British Spring Water",
        "Carbonated spring water",
        0.9,
        "water",
        ["its amazing!", "its terrible!"],
    )

    result = pretty_repr(example_namedtuple)

    print(result)
    assert (
        result
        == """StockKeepingUnit(
    name='Sparkling British Spring Water',
    description='Carbonated spring water',
    price=0.9,
    category='water',
    reviews=['its amazing!', 'its terrible!']
)"""
    )


def test_pretty_namedtuple_length_one_no_trailing_comma() -> None:
    instance = collections.namedtuple("Thing", ["name"])(name="Bob")
    assert pretty_repr(instance) == "Thing(name='Bob')"


def test_pretty_namedtuple_empty() -> None:
    instance = collections.namedtuple("Thing", [])()
    assert pretty_repr(instance) == "Thing()"


def test_pretty_namedtuple_custom_repr() -> None:
    _Thing = NamedTuple("_Thing", [])
    Thing = type("Thing", (_Thing,), {"__repr__": lambda self: "XX"})

    assert pretty_repr(Thing()) == "XX"


def test_pretty_namedtuple_fields_invalid_type() -> None:
    LooksLikeANamedTupleButIsnt = type(
        "LooksLikeANamedTupleButIsnt", (tuple,), {"_fields": "blah"}
    )

    instance = LooksLikeANamedTupleButIsnt()
    result = pretty_repr(instance)
    assert result == "()"  # Treated as tuple


def test_pretty_namedtuple_max_depth() -> None:
    instance = {"unit": StockKeepingUnit("a", "b", 1.0, "c", ["d", "e"])}
    result = pretty_repr(instance, max_depth=1)
    assert result == "{'unit': StockKeepingUnit(...)}"


def test_small_width() -> None:
    test = ["Hello world! 12345"]
    result = pretty_repr(test, max_width=10)
    expected = "[\n    'Hello world! 12345'\n]"
    assert result == expected


def test_ansi_in_pretty_repr() -> None:
    Hello = type("Hello", (), {"__repr__": lambda self: "Hello \x1b[38;5;239mWorld!"})

    pretty = Pretty(Hello())

    console = Console(file=io.StringIO(), record=True)
    console.print(pretty)
    result = console.export_text()

    assert result == "Hello World!\n"


def test_broken_repr() -> None:
    def _broken_repr(_self):
        1 / 0

    BrokenRepr = type("BrokenRepr", (), {"__repr__": _broken_repr})

    test = [BrokenRepr()]
    result = pretty_repr(test)
    expected = "[<repr-error 'division by zero'>]"
    assert result == expected


def test_broken_getattr() -> None:
    def _broken_getattr(_self, name):
        1 / 0

    BrokenAttr = type(
        "BrokenAttr",
        (),
        {"__getattr__": _broken_getattr, "__repr__": lambda self: "BrokenAttr()"},
    )

    test = BrokenAttr()
    result = pretty_repr(test)
    assert result == "BrokenAttr()"


def test_reference_cycle_container() -> None:
    test = []
    test.append(test)
    res = pretty_repr(test)
    assert res == "[...]"

    test = [1, []]
    test[1].append(test)
    res = pretty_repr(test)
    assert res == "[1, [...]]"

    # Not a cyclic reference, just a repeated reference
    a = [2]
    test = [1, [a, a]]
    res = pretty_repr(test)
    assert res == "[1, [[2], [2]]]"


def test_reference_cycle_namedtuple() -> None:
    Example = NamedTuple("Example", [("x", int), ("y", Any)])

    test = Example(1, [Example(2, [])])
    test.y[0].y.append(test)
    res = pretty_repr(test)
    assert res == "Example(x=1, y=[Example(x=2, y=[...])])"

    # Not a cyclic reference, just a repeated reference
    a = Example(2, None)
    test = Example(1, [a, a])
    res = pretty_repr(test)
    assert res == "Example(x=1, y=[Example(x=2, y=None), Example(x=2, y=None)])"


def _assert_reference_cycle_examples(example_factory) -> None:
    test = example_factory(1, None)
    test.y = test
    assert pretty_repr(test) == "Example(x=1, y=...)"

    test = example_factory(1, example_factory(2, None))
    test.y.y = test
    assert pretty_repr(test) == "Example(x=1, y=Example(x=2, y=...))"

    a = example_factory(2, None)
    test = example_factory(1, [a, a])
    assert pretty_repr(test) == (
        "Example(x=1, y=[Example(x=2, y=None), Example(x=2, y=None)])"
    )


def test_reference_cycle_dataclass() -> None:
    Example = make_dataclass("Example", [("x", int), ("y", Any)])

    _assert_reference_cycle_examples(Example)


def test_reference_cycle_attrs() -> None:
    Example = attr.make_class("Example", {"x": attr.field(), "y": attr.field()})

    _assert_reference_cycle_examples(Example)


def test_reference_cycle_custom_repr() -> None:
    def _example_init(self, x, y):
        self.x = x
        self.y = y

    def _example_rich_repr(self):
        yield ("x", self.x)
        yield ("y", self.y)

    Example = type(
        "Example",
        (),
        {"__init__": _example_init, "__rich_repr__": _example_rich_repr},
    )

    test = Example(1, None)
    test.y = test
    res = pretty_repr(test)
    assert res == "Example(x=1, y=...)"

    test = Example(1, Example(2, None))
    test.y.y = test
    res = pretty_repr(test)
    assert res == "Example(x=1, y=Example(x=2, y=...))"

    # Not a cyclic reference, just a repeated reference
    a = Example(2, None)
    test = Example(1, [a, a])
    res = pretty_repr(test)
    assert res == "Example(x=1, y=[Example(x=2, y=None), Example(x=2, y=None)])"


def test_max_depth() -> None:
    d = {}
    d["foo"] = {"fob": {"a": [1, 2, 3], "b": {"z": "x", "y": ["a", "b", "c"]}}}

    assert pretty_repr(d, max_depth=0) == "{...}"
    assert pretty_repr(d, max_depth=1) == "{'foo': {...}}"
    assert pretty_repr(d, max_depth=2) == "{'foo': {'fob': {...}}}"
    assert pretty_repr(d, max_depth=3) == "{'foo': {'fob': {'a': [...], 'b': {...}}}}"
    assert (
        pretty_repr(d, max_width=100, max_depth=4)
        == "{'foo': {'fob': {'a': [1, 2, 3], 'b': {'z': 'x', 'y': [...]}}}}"
    )
    assert (
        pretty_repr(d, max_width=100, max_depth=5)
        == "{'foo': {'fob': {'a': [1, 2, 3], 'b': {'z': 'x', 'y': ['a', 'b', 'c']}}}}"
    )
    assert (
        pretty_repr(d, max_width=100, max_depth=None)
        == "{'foo': {'fob': {'a': [1, 2, 3], 'b': {'z': 'x', 'y': ['a', 'b', 'c']}}}}"
    )


def test_max_depth_rich_repr() -> None:
    def _foo_init(self, foo):
        self.foo = foo

    def _foo_rich_repr(self):
        yield "foo", self.foo

    def _bar_init(self, bar):
        self.bar = bar

    def _bar_rich_repr(self):
        yield "bar", self.bar

    Foo = type("Foo", (), {"__init__": _foo_init, "__rich_repr__": _foo_rich_repr})
    Bar = type("Bar", (), {"__init__": _bar_init, "__rich_repr__": _bar_rich_repr})

    assert (
        pretty_repr(Foo(foo=Bar(bar=Foo(foo=[]))), max_depth=2)
        == "Foo(foo=Bar(bar=Foo(...)))"
    )


def test_max_depth_attrs() -> None:
    Foo = attr.make_class("Foo", {"foo": attr.field()})
    Bar = attr.make_class("Bar", {"bar": attr.field()})

    assert (
        pretty_repr(Foo(foo=Bar(bar=Foo(foo=[]))), max_depth=2)
        == "Foo(foo=Bar(bar=Foo(...)))"
    )


def test_max_depth_dataclass() -> None:
    Foo = make_dataclass("Foo", [("foo", object)])
    Bar = make_dataclass("Bar", [("bar", object)])

    assert (
        pretty_repr(Foo(foo=Bar(bar=Foo(foo=[]))), max_depth=2)
        == "Foo(foo=Bar(bar=Foo(...)))"
    )


def test_defaultdict() -> None:
    test_dict = defaultdict(int, {"foo": 2})
    result = pretty_repr(test_dict)
    assert result == "defaultdict(<class 'int'>, {'foo': 2})"


def test_deque() -> None:
    test_deque = deque([1, 2, 3])
    result = pretty_repr(test_deque)
    assert result == "deque([1, 2, 3])"
    test_deque = deque([1, 2, 3], maxlen=None)
    result = pretty_repr(test_deque)
    assert result == "deque([1, 2, 3])"
    test_deque = deque([1, 2, 3], maxlen=5)
    result = pretty_repr(test_deque)
    assert result == "deque([1, 2, 3], maxlen=5)"
    test_deque = deque([1, 2, 3], maxlen=0)
    result = pretty_repr(test_deque)
    assert result == "deque(maxlen=0)"
    test_deque = deque([])
    result = pretty_repr(test_deque)
    assert result == "deque()"
    test_deque = deque([], maxlen=None)
    result = pretty_repr(test_deque)
    assert result == "deque()"
    test_deque = deque([], maxlen=5)
    result = pretty_repr(test_deque)
    assert result == "deque(maxlen=5)"
    test_deque = deque([], maxlen=0)
    result = pretty_repr(test_deque)
    assert result == "deque(maxlen=0)"


def test_array() -> None:
    test_array = array("I", [1, 2, 3])
    result = pretty_repr(test_array)
    assert result == "array('I', [1, 2, 3])"


def test_tuple_of_one() -> None:
    assert pretty_repr((1,)) == "(1,)"


def test_node() -> None:
    node = Node("abc")
    assert pretty_repr(node) == "abc: "


def test_indent_lines() -> None:
    console = Console(width=100, color_system=None)
    console.begin_capture()
    console.print(Pretty([100, 200], indent_guides=True), width=8)
    expected = """\
[
│   100,
│   200
]
"""
    result = console.end_capture()
    print(repr(result))
    print(result)
    assert result == expected


def test_pprint() -> None:
    console = Console(color_system=None)
    console.begin_capture()
    pprint(1, console=console)
    assert console.end_capture() == "1\n"


def test_pprint_max_values() -> None:
    console = Console(color_system=None)
    console.begin_capture()
    pprint([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], console=console, max_length=2)
    assert console.end_capture() == "[1, 2, ... +8]\n"


def test_pprint_max_items() -> None:
    console = Console(color_system=None)
    console.begin_capture()
    pprint({"foo": 1, "bar": 2, "egg": 3}, console=console, max_length=2)
    assert console.end_capture() == """{'foo': 1, 'bar': 2, ... +1}\n"""


def test_pprint_max_string() -> None:
    console = Console(color_system=None)
    console.begin_capture()
    pprint(["Hello" * 20], console=console, max_string=8)
    assert console.end_capture() == """['HelloHel'+92]\n"""


def test_tuples() -> None:
    console = Console(color_system=None)
    console.begin_capture()
    pprint((1,), console=console)
    pprint((1,), expand_all=True, console=console)
    pprint(((1,),), expand_all=True, console=console)
    result = console.end_capture()
    print(repr(result))
    expected = "(1,)\n(\n│   1,\n)\n(\n│   (\n│   │   1,\n│   ),\n)\n"
    print(result)
    print("--")
    print(expected)
    assert result == expected


def test_newline() -> None:
    console = Console(color_system=None)
    console.begin_capture()
    console.print(Pretty((1,), insert_line=True, expand_all=True))
    result = console.end_capture()
    expected = "\n(\n    1,\n)\n"
    assert result == expected


def test_empty_repr() -> None:
    Foo = type("Foo", (), {"__repr__": lambda self: ""})

    assert pretty_repr(Foo()) == ""


def test_attrs() -> None:
    Point = attr.make_class(
        "Point",
        {
            "x": attr.field(),
            "y": attr.field(),
            "foo": attr.field(repr=str.upper),
            "z": attr.field(default=0),
        },
    )

    result = pretty_repr(Point(1, 2, foo="bar"))
    print(repr(result))
    expected = "Point(x=1, y=2, foo=BAR, z=0)"
    assert result == expected


def test_attrs_empty() -> None:
    Nada = attr.make_class("Nada", {})

    result = pretty_repr(Nada())
    print(repr(result))
    expected = "Nada()"
    assert result == expected


@skip_py310
@skip_py311
@skip_py312
@skip_py313
@skip_py314
def test_attrs_broken() -> None:
    Foo = attr.make_class("Foo", {"bar": attr.field()})

    foo = Foo(1)
    del foo.bar
    result = pretty_repr(foo)
    print(repr(result))
    expected = "Foo(bar=AttributeError('bar'))"
    assert result == expected


@skip_py38
@skip_py39
def test_attrs_broken_310() -> None:
    Foo = attr.make_class("Foo", {"bar": attr.field()})

    foo = Foo(1)
    del foo.bar
    result = pretty_repr(foo)
    print(repr(result))
    if sys.version_info >= (3, 13):
        expected = "Foo(\n    bar=AttributeError(\"'tests.test_pretty.test_attrs_broken_310.<locals>.Foo' object has no attribute 'bar'\")\n)"
    else:
        expected = "Foo(bar=AttributeError(\"'Foo' object has no attribute 'bar'\"))"
    assert result == expected


def test_user_dict() -> None:
    D1 = type("D1", (UserDict,), {})
    D2 = type("D2", (UserDict,), {"__repr__": lambda self: "FOO"})

    d1 = D1({"foo": "bar"})
    d2 = D2({"foo": "bar"})
    result = pretty_repr(d1, expand_all=True)
    print(repr(result))
    assert result == "{\n    'foo': 'bar'\n}"
    result = pretty_repr(d2, expand_all=True)
    print(repr(result))
    assert result == "FOO"


def test_lying_attribute() -> None:
    """Test getattr doesn't break rich repr protocol"""

    Foo = type("Foo", (), {"__getattr__": lambda self, attr: "foo"})

    foo = Foo()
    result = pretty_repr(foo)
    assert "Foo" in result


def test_measure_pretty() -> None:
    """Test measure respects expand_all"""
    # https://github.com/Textualize/rich/issues/1998
    console = Console()
    pretty = Pretty(["alpha", "beta", "delta", "gamma"], expand_all=True)

    measurement = console.measure(pretty)
    assert measurement == Measurement(12, 12)


def test_tuple_rich_repr() -> None:
    """
    Test that can use None as key to have tuple positional values.
    """

    def _foo_rich_repr(self):
        yield None, (1,)

    Foo = type("Foo", (), {"__rich_repr__": _foo_rich_repr})

    assert pretty_repr(Foo()) == "Foo((1,))"


def test_tuple_rich_repr_default() -> None:
    """
    Test that can use None as key to have tuple positional values and with a default.
    """

    def _foo_rich_repr(self):
        yield None, (1,), (1,)

    Foo = type("Foo", (), {"__rich_repr__": _foo_rich_repr})

    assert pretty_repr(Foo()) == "Foo()"


def test_dataclass_no_attribute() -> None:
    """Regression test for https://github.com/Textualize/rich/issues/3417"""
    BadDataclass = make_dataclass(
        "BadDataclass",
        [("item", int, field(init=False))],
        eq=False,
    )

    # item is not provided
    bad_data_class = BadDataclass()

    console = Console()
    with console.capture() as capture:
        console.print(bad_data_class)

    expected = "BadDataclass()\n"
    result = capture.get()
    assert result == expected
