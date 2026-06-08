"""Shared pretty-print traversal helpers (no dependency on pretty.Pretty)."""

from __future__ import annotations

import collections
import dataclasses
import inspect
import os
import reprlib
from array import array
from collections import Counter, UserDict, UserList, defaultdict, deque
from dataclasses import dataclass, is_dataclass
from inspect import isclass
from types import MappingProxyType
from typing import Any, Callable, DefaultDict, Deque, Dict, Iterable, List, Optional, Sequence, Tuple, Union

try:
    import attr as _attr_module

    _has_attrs = hasattr(_attr_module, "ib")
except ImportError:
    _has_attrs = False

from ._loop import loop_last
from .cells import cell_len

_dummy_namedtuple = collections.namedtuple("_dummy_namedtuple", [])


def _is_attr_object(obj: Any) -> bool:
    return _has_attrs and _attr_module.has(type(obj))


def _get_attr_fields(obj: Any) -> Sequence["_attr_module.Attribute[Any]"]:
    return _attr_module.fields(type(obj)) if _has_attrs else []


def _is_dataclass_repr(obj: object) -> bool:
    try:
        return obj.__repr__.__code__.co_filename in (
            dataclasses.__file__,
            reprlib.__file__,
        )
    except Exception:
        return False


def _has_default_namedtuple_repr(obj: object) -> bool:
    obj_file = None
    try:
        obj_file = inspect.getfile(obj.__repr__)
    except (OSError, TypeError):
        pass
    default_repr_file = inspect.getfile(_dummy_namedtuple.__repr__)
    return obj_file == default_repr_file


def _safe_isinstance(
    obj: object, class_or_tuple: Union[type, Tuple[type, ...]]
) -> bool:
    try:
        return isinstance(obj, class_or_tuple)
    except Exception:
        return False


def _get_braces_for_defaultdict(_object: DefaultDict[Any, Any]) -> Tuple[str, str, str]:
    return (
        f"defaultdict({_object.default_factory!r}, {{",
        "})",
        f"defaultdict({_object.default_factory!r}, {{}})",
    )


def _get_braces_for_deque(_object: Deque[Any]) -> Tuple[str, str, str]:
    if _object.maxlen is None:
        return ("deque([", "])", "deque()")
    return ("deque([", f"], maxlen={_object.maxlen})", f"deque(maxlen={_object.maxlen})")


def _get_braces_for_array(_object: "array[Any]") -> Tuple[str, str, str]:
    return (f"array({_object.typecode!r}, [", "])", f"array({_object.typecode!r})")


_BRACES: Dict[type, Callable[[Any], Tuple[str, str, str]]] = {
    os._Environ: lambda _object: ("environ({", "})", "environ({})"),
    array: _get_braces_for_array,
    defaultdict: _get_braces_for_defaultdict,
    Counter: lambda _object: ("Counter({", "})", "Counter()"),
    deque: _get_braces_for_deque,
    dict: lambda _object: ("{", "}", "{}"),
    UserDict: lambda _object: ("{", "}", "{}"),
    frozenset: lambda _object: ("frozenset({", "})", "frozenset()"),
    list: lambda _object: ("[", "]", "[]"),
    UserList: lambda _object: ("[", "]", "[]"),
    set: lambda _object: ("{", "}", "set()"),
    tuple: lambda _object: ("(", ")", "()"),
    MappingProxyType: lambda _object: ("mappingproxy({", "})", "mappingproxy({})"),
}
_CONTAINERS = tuple(_BRACES.keys())
_MAPPING_CONTAINERS = (dict, os._Environ, MappingProxyType, UserDict)


@dataclass
class Node:
    """A node in a repr tree. May be atomic or a container."""

    key_repr: str = ""
    value_repr: str = ""
    open_brace: str = ""
    close_brace: str = ""
    empty: str = ""
    last: bool = False
    is_tuple: bool = False
    is_namedtuple: bool = False
    children: Optional[List["Node"]] = None
    key_separator: str = ": "
    separator: str = ", "

    def _iter_child_tokens(self) -> Iterable[str]:
        if not self.children:
            yield self.empty
            return
        yield self.open_brace
        yield from self._iter_child_token_items()
        yield self.close_brace

    def _iter_child_token_items(self) -> Iterable[str]:
        if self.is_tuple and (not self.is_namedtuple) and (len(self.children) == 1):
            yield from self.children[0].iter_tokens()
            yield ","
            return
        for child in self.children:
            yield from child.iter_tokens()
            if not child.last:
                yield self.separator

    def iter_tokens(self) -> Iterable[str]:
        if self.key_repr:
            yield self.key_repr
            yield self.key_separator
        if self.value_repr:
            yield self.value_repr
        elif self.children is not None:
            yield from self._iter_child_tokens()

    def check_length(self, start_length: int, max_length: int) -> bool:
        total_length = start_length
        for token in self.iter_tokens():
            total_length += cell_len(token)
            if total_length > max_length:
                return False
        return True

    def __str__(self) -> str:
        return "".join(self.iter_tokens())

    def render(
        self, max_width: int = 80, indent_size: int = 4, expand_all: bool = False
    ) -> str:
        lines = [_Line(node=self, is_root=True)]
        line_no = 0
        while line_no < len(lines):
            line = lines[line_no]
            if line.expandable and (not line.expanded):
                if expand_all or not line.check_length(max_width):
                    lines[line_no : line_no + 1] = line.expand(indent_size)
            line_no += 1
        return "\n".join(str(line) for line in lines)


@dataclass
class _Line:
    parent: Optional["_Line"] = None
    is_root: bool = False
    node: Optional[Node] = None
    text: str = ""
    suffix: str = ""
    whitespace: str = ""
    expanded: bool = False
    last: bool = False

    @property
    def expandable(self) -> bool:
        return bool(self.node is not None and self.node.children)

    def check_length(self, max_length: int) -> bool:
        start_length = len(self.whitespace) + cell_len(self.text) + cell_len(self.suffix)
        assert self.node is not None
        return self.node.check_length(start_length, max_length)

    def expand(self, indent_size: int) -> Iterable["_Line"]:
        node = self.node
        assert node is not None
        whitespace = self.whitespace
        assert node.children
        if node.key_repr:
            new_line = yield _Line(
                text=f"{node.key_repr}{node.key_separator}{node.open_brace}",
                whitespace=whitespace,
            )
        else:
            new_line = yield _Line(text=node.open_brace, whitespace=whitespace)
        child_whitespace = self.whitespace + " " * indent_size
        tuple_of_one = node.is_tuple and len(node.children) == 1
        for last, child in loop_last(node.children):
            separator = "," if tuple_of_one else node.separator
            line = _Line(
                parent=new_line,
                node=child,
                whitespace=child_whitespace,
                suffix=separator,
                last=last and (not tuple_of_one),
            )
            yield line
        yield _Line(
            text=node.close_brace,
            whitespace=whitespace,
            suffix=self.suffix,
            last=self.last,
        )

    def __str__(self) -> str:
        if self.last:
            return f"{self.whitespace}{self.text}{self.node or ''}"
        return f"{self.whitespace}{self.text}{self.node or ''}{self.suffix.rstrip()}"


def _is_namedtuple(obj: Any) -> bool:
    try:
        fields = getattr(obj, "_fields", None)
    except Exception:
        return False
    return isinstance(obj, tuple) and isinstance(fields, tuple)


def _iter_rich_repr_args(rich_args: Any) -> Iterable[Union[Any, Tuple[str, Any]]]:
    for arg in rich_args:
        if not _safe_isinstance(arg, tuple):
            yield arg
            continue
        if len(arg) == 3:
            key, child, default = arg
            if default != child:
                yield (key, child)
        elif len(arg) == 2:
            key, child = arg
            yield (key, child)
        elif len(arg) == 1:
            yield arg[0]


def _iter_attr_field_values(
    obj: Any, attr_fields: Sequence["_attr_module.Attribute[Any]"]
) -> Iterable[Tuple[str, Any, Optional[Callable[[Any], str]]]]:
    for attr in attr_fields:
        if not attr.repr:
            continue
        try:
            value = getattr(obj, attr.name)
        except Exception as error:
            yield (attr.name, error, None)
        else:
            yield (attr.name, value, attr.repr if callable(attr.repr) else None)
