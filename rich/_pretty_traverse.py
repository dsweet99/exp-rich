"""Object traversal for pretty printing."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from inspect import isclass
from itertools import islice
from typing import Any, Callable, List, Optional, Set

from rich.repr import RichReprResult

from ._loop import loop_last
from ._pretty_common import (
    Node,
    _BRACES,
    _CONTAINERS,
    _MAPPING_CONTAINERS,
    _get_attr_fields,
    _has_default_namedtuple_repr,
    _is_attr_object,
    _is_dataclass_repr,
    _is_namedtuple,
    _iter_attr_field_values,
    _iter_rich_repr_args,
    _safe_isinstance,
)


@dataclass
class _TraverseState:
    max_length: Optional[int]
    max_string: Optional[int]
    max_depth: Optional[int]
    visited_ids: Set[int]
    traverse: Callable[..., Node]


def _to_repr(max_string: Optional[int], obj: Any) -> str:
    if max_string is not None and _safe_isinstance(obj, (bytes, str)):
        if len(obj) > max_string:
            truncated = len(obj) - max_string
            return f"{obj[:max_string]!r}+{truncated}"
    try:
        return repr(obj)
    except Exception as error:
        return f"<repr-error {str(error)!r}>"


def _object_has_fake_attributes(obj: Any) -> bool:
    try:
        return hasattr(obj, "awehoi234_wdfjwljet234_234wdfoijsdfmmnxpi492")
    except Exception:
        return False


def _rich_repr_result(obj: Any, fake_attributes: bool) -> Optional[RichReprResult]:
    if fake_attributes:
        return None
    try:
        if hasattr(obj, "__rich_repr__") and not isclass(obj):
            return obj.__rich_repr__()
    except Exception:
        return None
    return None


def _traverse_rich_repr(
    obj: Any,
    state: _TraverseState,
    *,
    root: bool,
    depth: int,
    reached_max_depth: bool,
    rich_repr_result: RichReprResult,
) -> Node:
    state.visited_ids.add(id(obj))
    angular = getattr(obj.__rich_repr__, "angular", False)
    args = list(_iter_rich_repr_args(rich_repr_result))
    class_name = obj.__class__.__name__
    if not args:
        node = Node(
            value_repr=f"<{class_name}>" if angular else f"{class_name}()",
            children=[],
            last=root,
        )
        state.visited_ids.remove(id(obj))
        return node

    children: List[Node] = []
    if reached_max_depth:
        node = Node(
            value_repr=f"<{class_name}...>" if angular else f"{class_name}(...)"
        )
        state.visited_ids.remove(id(obj))
        return node

    if angular:
        node = Node(
            open_brace=f"<{class_name} ",
            close_brace=">",
            children=children,
            last=root,
            separator=" ",
        )
    else:
        node = Node(
            open_brace=f"{class_name}(",
            close_brace=")",
            children=children,
            last=root,
        )
    append = children.append
    _traverse_rich_repr_append_args(
        state, args, append, depth=depth
    )
    state.visited_ids.remove(id(obj))
    return node


def _traverse_rich_repr_append_args(
    state: _TraverseState,
    args: list,
    append,
    *,
    depth: int,
) -> None:
    for last, arg in loop_last(args):
        if _safe_isinstance(arg, tuple):
            key, child = arg
            child_node = state.traverse(child, depth=depth + 1)
            child_node.key_repr = key
            child_node.key_separator = "="
        else:
            child_node = state.traverse(arg, depth=depth + 1)
        child_node.last = last
        append(child_node)


def _traverse_attr_object(
    obj: Any,
    state: _TraverseState,
    *,
    root: bool,
    depth: int,
    reached_max_depth: bool,
) -> Node:
    state.visited_ids.add(id(obj))
    children: List[Node] = []
    attr_fields = _get_attr_fields(obj)
    if not attr_fields:
        node = Node(value_repr=f"{obj.__class__.__name__}()", children=[], last=root)
        state.visited_ids.remove(id(obj))
        return node
    if reached_max_depth:
        node = Node(value_repr=f"{obj.__class__.__name__}(...)")
        state.visited_ids.remove(id(obj))
        return node

    node = Node(
        open_brace=f"{obj.__class__.__name__}(",
        close_brace=")",
        children=children,
        last=root,
    )
    append = children.append
    for last, (name, value, repr_callable) in loop_last(
        _iter_attr_field_values(obj, attr_fields)
    ):
        if repr_callable:
            child_node = Node(value_repr=str(repr_callable(value)))
        else:
            child_node = state.traverse(value, depth=depth + 1)
        child_node.last = last
        child_node.key_repr = name
        child_node.key_separator = "="
        append(child_node)
    state.visited_ids.remove(id(obj))
    return node


def _traverse_dataclass_object(
    obj: Any,
    state: _TraverseState,
    *,
    root: bool,
    depth: int,
    reached_max_depth: bool,
) -> Node:
    state.visited_ids.add(id(obj))
    children: List[Node] = []
    if reached_max_depth:
        node = Node(value_repr=f"{obj.__class__.__name__}(...)")
        state.visited_ids.remove(id(obj))
        return node

    node = Node(
        open_brace=f"{obj.__class__.__name__}(",
        close_brace=")",
        children=children,
        last=root,
        empty=f"{obj.__class__.__name__}()",
    )
    append = children.append
    for last, field in loop_last(
        field for field in fields(obj) if field.repr and hasattr(obj, field.name)
    ):
        child_node = state.traverse(getattr(obj, field.name), depth=depth + 1)
        child_node.key_repr = field.name
        child_node.last = last
        child_node.key_separator = "="
        append(child_node)
    state.visited_ids.remove(id(obj))
    return node


def _traverse_namedtuple_object(
    obj: Any,
    state: _TraverseState,
    *,
    root: bool,
    depth: int,
    reached_max_depth: bool,
) -> Node:
    state.visited_ids.add(id(obj))
    class_name = obj.__class__.__name__
    if reached_max_depth:
        node = Node(value_repr=f"{class_name}(...)")
        state.visited_ids.remove(id(obj))
        return node

    children: List[Node] = []
    node = Node(
        open_brace=f"{class_name}(",
        close_brace=")",
        children=children,
        empty=f"{class_name}()",
    )
    append = children.append
    for last, (key, value) in loop_last(obj._asdict().items()):
        child_node = state.traverse(value, depth=depth + 1)
        child_node.key_repr = key
        child_node.last = last
        child_node.key_separator = "="
        append(child_node)
    state.visited_ids.remove(id(obj))
    return node


def _traverse_container_items(
    obj: Any,
    state: _TraverseState,
    *,
    depth: int,
    children: List[Node],
    last_item_index: int,
) -> None:
    append = children.append
    if _safe_isinstance(obj, _MAPPING_CONTAINERS):
        iter_items = iter(obj.items())
        if state.max_length is not None:
            iter_items = islice(iter_items, state.max_length)
        for index, (key, child) in enumerate(iter_items):
            child_node = state.traverse(child, depth=depth + 1)
            child_node.key_repr = _to_repr(state.max_string, key)
            child_node.last = index == last_item_index
            append(child_node)
        return

    iter_values = iter(obj)
    if state.max_length is not None:
        iter_values = islice(iter_values, state.max_length)
    for index, child in enumerate(iter_values):
        child_node = state.traverse(child, depth=depth + 1)
        child_node.last = index == last_item_index
        append(child_node)


def _traverse_container_object(
    obj: Any,
    state: _TraverseState,
    *,
    root: bool,
    depth: int,
    reached_max_depth: bool,
) -> Node:
    obj_type = next(
        container_type
        for container_type in _CONTAINERS
        if _safe_isinstance(obj, container_type)
    )
    state.visited_ids.add(id(obj))
    open_brace, close_brace, empty = _BRACES[obj_type](obj)
    if reached_max_depth:
        node = Node(value_repr=f"{open_brace}...{close_brace}")
        state.visited_ids.remove(id(obj))
        return node
    if obj_type.__repr__ != type(obj).__repr__:
        node = Node(value_repr=_to_repr(state.max_string, obj), last=root)
        state.visited_ids.remove(id(obj))
        return node
    if not obj:
        node = Node(empty=empty, children=[], last=root)
        state.visited_ids.remove(id(obj))
        return node

    children: List[Node] = []
    node = Node(
        open_brace=open_brace,
        close_brace=close_brace,
        children=children,
        last=root,
    )
    num_items = len(obj)
    _traverse_container_items(
        obj, state, depth=depth, children=children, last_item_index=num_items - 1
    )
    if state.max_length is not None and num_items > state.max_length:
        children.append(
            Node(value_repr=f"... +{num_items - state.max_length}", last=True)
        )
    state.visited_ids.remove(id(obj))
    return node


def _do_traverse(
    obj: Any,
    state: _TraverseState,
    *,
    root: bool = False,
    depth: int = 0,
) -> Node:
    if id(obj) in state.visited_ids:
        return Node(value_repr="...")

    reached_max_depth = state.max_depth is not None and depth >= state.max_depth
    fake_attributes = _object_has_fake_attributes(obj)
    rich_repr_result = _rich_repr_result(obj, fake_attributes)

    if rich_repr_result is not None:
        node = _traverse_rich_repr(
            obj,
            state,
            root=root,
            depth=depth,
            reached_max_depth=reached_max_depth,
            rich_repr_result=rich_repr_result,
        )
    elif _is_attr_object(obj) and not fake_attributes:
        node = _traverse_attr_object(
            obj, state, root=root, depth=depth, reached_max_depth=reached_max_depth
        )
    elif (
        is_dataclass(obj)
        and not _safe_isinstance(obj, type)
        and not fake_attributes
        and _is_dataclass_repr(obj)
    ):
        node = _traverse_dataclass_object(
            obj, state, root=root, depth=depth, reached_max_depth=reached_max_depth
        )
    elif _is_namedtuple(obj) and _has_default_namedtuple_repr(obj):
        node = _traverse_namedtuple_object(
            obj, state, root=root, depth=depth, reached_max_depth=reached_max_depth
        )
    elif _safe_isinstance(obj, _CONTAINERS):
        node = _traverse_container_object(
            obj, state, root=root, depth=depth, reached_max_depth=reached_max_depth
        )
    else:
        node = Node(value_repr=_to_repr(state.max_string, obj), last=root)

    node.is_tuple = type(obj) == tuple
    node.is_namedtuple = _is_namedtuple(obj)
    return node


def traverse_object(
    _object: Any,
    max_length: Optional[int] = None,
    max_string: Optional[int] = None,
    max_depth: Optional[int] = None,
) -> Node:
    """Traverse object and generate a tree."""
    visited_ids: Set[int] = set()
    state = _TraverseState(
        max_length=max_length,
        max_string=max_string,
        max_depth=max_depth,
        visited_ids=visited_ids,
        traverse=lambda *args, **kwargs: _do_traverse(*args, state=state, **kwargs),
    )
    return _do_traverse(_object, state, root=True)
