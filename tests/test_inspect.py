import io
import sys
from types import ModuleType
from typing import Sequence, Type

import pytest

from tests._inspect_fixtures import (
    BrokenCallFoo,
    Foo,
    FooSubclass,
    KlassWithQualnameSlots,
    ModuleThing,
    Something,
    SwigThing,
    _FIXTURES_MODULE,
)
from tests._inspect_render import (
    console_class,
    get_object_types_mro,
    get_object_types_mro_as_strings,
    inspect_module,
    is_object_one_of_types,
    render,
)

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


skip_pypy3 = pytest.mark.skipif(
    hasattr(sys, "pypy_version_info"),
    reason="rendered differently on pypy3",
)


def test_render():
    Console = console_class()
    inspect = inspect_module()

    console = Console(width=100, file=io.StringIO(), legacy_windows=False)

    foo = Foo("hello")
    inspect(foo, console=console, all=True, value=False)
    result = console.file.getvalue()
    print(repr(result))
    expected = "╭─────────── <class 'tests._inspect_fixtures.Foo'> ────────────╮\n│ Foo test                                                     │\n│                                                              │\n│   broken = InspectError()                                    │\n│ __init__ = def __init__(foo: int) -> None: constructor docs. │\n│   method = def method(a, b) -> str: Multi line               │\n╰──────────────────────────────────────────────────────────────╯\n"
    assert result == expected


@skip_pypy3
def test_inspect_text():
    num_attributes = 34 if sys.version_info >= (3, 11) else 33
    expected = (
        "╭──────────────── <class 'str'> ─────────────────╮\n"
        "│ str(object='') -> str                          │\n"
        "│ str(bytes_or_buffer[, encoding[, errors]]) ->  │\n"
        "│ str                                            │\n"
        "│                                                │\n"
        f"│ {num_attributes} attribute(s) not shown. Run                 │\n"
        "│ inspect(inspect) for options.                  │\n"
        "╰────────────────────────────────────────────────╯\n"
    )
    print(repr(expected))
    assert render("Hello") == expected


@skip_pypy3
def test_inspect_empty_dict():
    expected = (
        "╭──────────────── <class 'dict'> ────────────────╮\n"
        "│ dict() -> new empty dictionary                 │\n"
        "│ dict(mapping) -> new dictionary initialized    │\n"
        "│ from a mapping object's                        │\n"
        "│     (key, value) pairs                         │\n"
        "│ dict(iterable) -> new dictionary initialized   │\n"
        "│ as if via:                                     │\n"
        "│     d = {}                                     │\n"
        "│     for k, v in iterable:                      │\n"
        "│         d[k] = v                               │\n"
        "│ dict(**kwargs) -> new dictionary initialized   │\n"
        "│ with the name=value pairs                      │\n"
        "│     in the keyword argument list.  For         │\n"
        "│ example:  dict(one=1, two=2)                   │\n"
        "│                                                │\n"
    )
    assert render({}).startswith(expected)


@skip_py314
@skip_py313
@skip_py312
@skip_py311
@skip_pypy3
def test_inspect_builtin_function_except_python311():
    # Pre-3.11 Python versions - print builtin has no signature available
    expected = (
        "╭────────── <built-in function print> ───────────╮\n"
        "│ def print(...)                                 │\n"
        "│                                                │\n"
        "│ print(value, ..., sep=' ', end='\\n',           │\n"
        "│ file=sys.stdout, flush=False)                  │\n"
        "│                                                │\n"
        "│ 29 attribute(s) not shown. Run                 │\n"
        "│ inspect(inspect) for options.                  │\n"
        "╰────────────────────────────────────────────────╯\n"
    )
    assert render(print) == expected


@pytest.mark.skipif(
    sys.version_info < (3, 11), reason="print builtin signature only available on 3.11+"
)
@skip_pypy3
def test_inspect_builtin_function_only_python311():
    # On 3.11, the print builtin *does* have a signature, unlike in prior versions
    expected = (
        "╭────────── <built-in function print> ───────────╮\n"
        "│ def print(*args, sep=' ', end='\\n', file=None, │\n"
        "│ flush=False):                                  │\n"
        "│                                                │\n"
        "│ Prints the values to a stream, or to           │\n"
        "│ sys.stdout by default.                         │\n"
        "│                                                │\n"
        "│ 30 attribute(s) not shown. Run                 │\n"
        "│ inspect(inspect) for options.                  │\n"
        "╰────────────────────────────────────────────────╯\n"
    )
    assert render(print) == expected


@skip_pypy3
def test_inspect_coroutine():
    async def coroutine():
        pass

    expected = (
        "╭─ <function test_inspect_coroutine.<locals>.cor─╮\n"
        "│ async def                                      │\n"
        "│ test_inspect_coroutine.<locals>.coroutine():   │\n"
    )
    assert render(coroutine).startswith(expected)


def test_inspect_integer():
    expected = (
        "╭────── <class 'int'> ───────╮\n"
        "│ int([x]) -> integer        │\n"
        "│ int(x, base=10) -> integer │\n"
        "│                            │\n"
        "│ denominator = 1            │\n"
        "│        imag = 0            │\n"
        "│   numerator = 1            │\n"
        "│        real = 1            │\n"
        "╰────────────────────────────╯\n"
    )
    assert expected == render(1)


def test_inspect_integer_with_value():
    expected = "╭────── <class 'int'> ───────╮\n│ int([x]) -> integer        │\n│ int(x, base=10) -> integer │\n│                            │\n│ ╭────────────────────────╮ │\n│ │ 1                      │ │\n│ ╰────────────────────────╯ │\n│                            │\n│ denominator = 1            │\n│        imag = 0            │\n│   numerator = 1            │\n│        real = 1            │\n╰────────────────────────────╯\n"
    value = render(1, value=True)
    print(repr(value))
    assert value == expected


_INT_METHODS_PREFIX = (
    "╭──────────────── <class 'int'> ─────────────────╮\n"
    "│ int([x]) -> integer                            │\n"
    "│ int(x, base=10) -> integer                     │\n"
    "│                                                │\n"
    "│      denominator = 1                           │\n"
    "│             imag = 0                           │\n"
    "│        numerator = 1                           │\n"
    "│             real = 1                           │\n"
    "│ as_integer_ratio = def as_integer_ratio():     │\n"
    "│                    Return integer ratio.       │\n"
)


def _assert_int_methods_render(method_lines: str) -> None:
    expected = (
        _INT_METHODS_PREFIX
        + method_lines
        + "╰────────────────────────────────────────────────╯\n"
    )
    assert render(1, methods=True) == expected


@skip_py310
@skip_py311
@skip_py312
@skip_py313
@skip_py314
def test_inspect_integer_with_methods_python38_and_python39():
    _assert_int_methods_render(
        "│       bit_length = def bit_length(): Number of │\n"
        "│                    bits necessary to represent │\n"
        "│                    self in binary.             │\n"
        "│        conjugate = def conjugate(...) Returns  │\n"
        "│                    self, the complex conjugate │\n"
        "│                    of any int.                 │\n"
        "│       from_bytes = def from_bytes(bytes,       │\n"
        "│                    byteorder, *,               │\n"
        "│                    signed=False): Return the   │\n"
        "│                    integer represented by the  │\n"
        "│                    given array of bytes.       │\n"
        "│         to_bytes = def to_bytes(length,        │\n"
        "│                    byteorder, *,               │\n"
        "│                    signed=False): Return an    │\n"
        "│                    array of bytes representing │\n"
        "│                    an integer.                 │\n"
    )


_py310_only = pytest.mark.skipif(
    sys.version_info[:2] != (3, 10), reason="3.10 only"
)
_py311_only = pytest.mark.skipif(
    sys.version_info[:2] != (3, 11), reason="3.11 only"
)


@skip_py38
@skip_py39
@skip_py312
@skip_py313
@skip_py314
@pytest.mark.parametrize(
    "method_lines",
    [
        pytest.param(
            "│        bit_count = def bit_count(): Number of  │\n"
            "│                    ones in the binary          │\n"
            "│                    representation of the       │\n"
            "│                    absolute value of self.     │\n"
            "│       bit_length = def bit_length(): Number of │\n"
            "│                    bits necessary to represent │\n"
            "│                    self in binary.             │\n"
            "│        conjugate = def conjugate(...) Returns  │\n"
            "│                    self, the complex conjugate │\n"
            "│                    of any int.                 │\n"
            "│       from_bytes = def from_bytes(bytes,       │\n"
            "│                    byteorder, *,               │\n"
            "│                    signed=False): Return the   │\n"
            "│                    integer represented by the  │\n"
            "│                    given array of bytes.       │\n"
            "│         to_bytes = def to_bytes(length,        │\n"
            "│                    byteorder, *,               │\n"
            "│                    signed=False): Return an    │\n"
            "│                    array of bytes representing │\n"
            "│                    an integer.                 │\n",
            marks=_py310_only,
        ),
        pytest.param(
            "│        bit_count = def bit_count(): Number of  │\n"
            "│                    ones in the binary          │\n"
            "│                    representation of the       │\n"
            "│                    absolute value of self.     │\n"
            "│       bit_length = def bit_length(): Number of │\n"
            "│                    bits necessary to represent │\n"
            "│                    self in binary.             │\n"
            "│        conjugate = def conjugate(...) Returns  │\n"
            "│                    self, the complex conjugate │\n"
            "│                    of any int.                 │\n"
            "│       from_bytes = def from_bytes(bytes,       │\n"
            "│                    byteorder='big', *,         │\n"
            "│                    signed=False): Return the   │\n"
            "│                    integer represented by the  │\n"
            "│                    given array of bytes.       │\n"
            "│         to_bytes = def to_bytes(length=1,      │\n"
            "│                    byteorder='big', *,         │\n"
            "│                    signed=False): Return an    │\n"
            "│                    array of bytes representing │\n"
            "│                    an integer.                 │\n",
            marks=_py311_only,
        ),
    ],
)
def test_inspect_integer_with_methods_python310_and_311(method_lines: str):
    _assert_int_methods_render(method_lines)


@skip_pypy3
def test_broken_call_attr():
    foo = BrokenCallFoo()
    assert callable(foo.foo)
    expected = "╭─ <class 'tests._inspect_fixtures.BrokenCallFoo'> ─╮\n│ foo = NotCallable()                               │\n╰───────────────────────────────────────────────────╯\n"
    result = render(foo, methods=True, width=100)
    print(repr(result))
    assert expected == result


def test_inspect_swig_edge_case():
    """Issue #1838 - Edge case with Faiss library - object with empty dir()"""
    thing = SwigThing()
    try:
        inspect_module()(thing)
    except Exception as e:
        assert False, f"Object with no __class__ shouldn't raise {e}"


def test_inspect_module_with_class():
    def function():
        pass

    module = ModuleType("my_module")
    module.SomeClass = ModuleThing
    module.function = function

    expected = (
        "╭────────── <module 'my_module'> ──────────╮\n"
        "│  function = def function():              │\n"
        "│ SomeClass = class SomeClass(): Docstring │\n"
        "╰──────────────────────────────────────────╯\n"
    )
    assert render(module, methods=True) == expected


def test_qualname_in_slots():
    try:
        inspect_module()(KlassWithQualnameSlots)
    except Exception as e:
        assert False, f"Class with __qualname__ in __slots__ shouldn't raise {e}"


@pytest.mark.parametrize(
    "special_character,expected_replacement",
    (
        ("\a", "\\a"),
        ("\b", "\\b"),
        ("\f", "\\f"),
        ("\r", "\\r"),
        ("\v", "\\v"),
    ),
)
def test_can_handle_special_characters_in_docstrings(
    special_character: str, expected_replacement: str
) -> None:
    Something.Thing.__doc__ = f"""
    Multiline docstring
    with {special_character} should be handled
    """

    expected = """\
╭─ <class 'tests._inspect_fixtures.Something'> ─╮
│ class Something():                            │
│                                               │
│ Thing = class Thing():                        │
│         Multiline docstring                   │
│         with %s should be handled             │
╰───────────────────────────────────────────────╯
""" % (
        expected_replacement
    )
    assert render(Something, methods=True) == expected


@pytest.mark.parametrize(
    "obj,expected_result",
    (
        [object, (object,)],
        [object(), (object,)],
        ["hi", (str, object)],
        [str, (str, object)],
        [Foo(1), (Foo, object)],
        [Foo, (Foo, object)],
        [FooSubclass(1), (FooSubclass, Foo, object)],
        [FooSubclass, (FooSubclass, Foo, object)],
    ),
)
def test_object_types_mro(obj: object, expected_result: Sequence[Type]):
    assert get_object_types_mro(obj) == expected_result


@pytest.mark.parametrize(
    "obj,expected_result",
    (
        # fmt: off
        ["hi", ["builtins.str", "builtins.object"]],
        [str, ["builtins.str", "builtins.object"]],
        [Foo(1), [f"{_FIXTURES_MODULE}.Foo", "builtins.object"]],
        [Foo, [f"{_FIXTURES_MODULE}.Foo", "builtins.object"]],
        [FooSubclass(1),
         [f"{_FIXTURES_MODULE}.FooSubclass", f"{_FIXTURES_MODULE}.Foo", "builtins.object"]],
        [FooSubclass,
         [f"{_FIXTURES_MODULE}.FooSubclass", f"{_FIXTURES_MODULE}.Foo", "builtins.object"]],
        # fmt: on
    ),
)
def test_object_types_mro_as_strings(obj: object, expected_result: Sequence[str]):
    assert get_object_types_mro_as_strings(obj) == expected_result


@pytest.mark.parametrize(
    "obj,types,expected_result",
    (
        # fmt: off
        ["hi", ["builtins.str"], True],
        [str, ["builtins.str"], True],
        ["hi", ["builtins.str", "foo"], True],
        [str, ["builtins.str", "foo"], True],
        [Foo(1), [f"{_FIXTURES_MODULE}.Foo"], True],
        [Foo, [f"{_FIXTURES_MODULE}.Foo"], True],
        [Foo(1), ["builtins.str", f"{_FIXTURES_MODULE}.Foo"], True],
        [Foo, ["builtins.int", f"{_FIXTURES_MODULE}.Foo"], True],
        [Foo(1), [f"{_FIXTURES_MODULE}.FooSubclass"], False],
        [Foo, [f"{_FIXTURES_MODULE}.FooSubclass"], False],
        [Foo(1), [f"{_FIXTURES_MODULE}.FooSubclass", f"{_FIXTURES_MODULE}.Foo"], True],
        [Foo, [f"{_FIXTURES_MODULE}.Foo", f"{_FIXTURES_MODULE}.FooSubclass"], True],
        # fmt: on
    ),
)
def test_object_is_one_of_types(
    obj: object, types: Sequence[str], expected_result: bool
):
    assert is_object_one_of_types(obj, types) is expected_result
