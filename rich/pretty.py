from __future__ import annotations

import builtins
import collections
import dataclasses
import inspect
import os
import reprlib
import sys
from array import array
from collections import Counter, UserDict, UserList, defaultdict, deque
from dataclasses import fields, is_dataclass
from inspect import isclass
from itertools import islice
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    DefaultDict,
    Deque,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

from ._pick import M_CONSOLE, M_CONSOLE_WRITE, M_JUPYTER_HTML, M_MEASURE, M_TEXT, rich_module
from .repr import RichReprResult

try:
    import attr as _attr_module

    _has_attrs = hasattr(_attr_module, "ib")
except ImportError:  # pragma: no cover
    _has_attrs = False

from ._loop import loop_last
from ._pick import pick_bool
from .abc import RichRenderable
from .cells import cell_len

if TYPE_CHECKING:
    from ._types import Console, ConsoleOptions, HighlighterType, JustifyMethod, Measurement, OverflowMethod, RenderResult



def _default_repr_highlighter() -> "HighlighterType":
    from .highlighter import ReprHighlighter

    return ReprHighlighter()

def _is_attr_object(obj: Any) -> bool:
    """Check if an object was created with attrs module."""
    return _has_attrs and _attr_module.has(type(obj))


def _get_attr_fields(obj: Any) -> Sequence["_attr_module.Attribute[Any]"]:
    """Get fields for an attrs object."""
    return _attr_module.fields(type(obj)) if _has_attrs else []


def _is_dataclass_repr(obj: object) -> bool:
    """Check if an instance of a dataclass contains the default repr.

    Args:
        obj (object): A dataclass instance.

    Returns:
        bool: True if the default repr is used, False if there is a custom repr.
    """
    # Digging in to a lot of internals here
    # Catching all exceptions in case something is missing on a non CPython implementation
    try:
        return obj.__repr__.__code__.co_filename in (
            dataclasses.__file__,
            reprlib.__file__,
        )
    except Exception:  # pragma: no coverage
        return False


_dummy_namedtuple = collections.namedtuple("_dummy_namedtuple", [])


def _has_default_namedtuple_repr(obj: object) -> bool:
    """Check if an instance of namedtuple contains the default repr

    Args:
        obj (object): A namedtuple

    Returns:
        bool: True if the default repr is used, False if there's a custom repr.
    """
    obj_file = None
    try:
        obj_file = inspect.getfile(obj.__repr__)
    except (OSError, TypeError):
        # OSError handles case where object is defined in __main__ scope, e.g. REPL - no filename available.
        # TypeError trapped defensively, in case of object without filename slips through.
        pass
    default_repr_file = inspect.getfile(_dummy_namedtuple.__repr__)
    return obj_file == default_repr_file


def _ipy_display_hook(
    value: Any,
    console: Optional["Console"] = None,
    overflow: "OverflowMethod" = "ignore",
    crop: bool = False,
    indent_guides: bool = False,
    max_length: Optional[int] = None,
    max_string: Optional[int] = None,
    max_depth: Optional[int] = None,
    expand_all: bool = False,
) -> Union[str, None]:
    # always skip rich generated jupyter renderables or None values
    ConsoleRenderable = rich_module(M_CONSOLE).ConsoleRenderable
    JupyterRenderable = rich_module(M_JUPYTER_HTML).JupyterRenderable
    if _safe_isinstance(value, JupyterRenderable) or value is None:
        return None

    console = console or rich_module(M_CONSOLE).get_console()

    with console.capture() as capture:
        # certain renderables should start on a new line
        if _safe_isinstance(value, ConsoleRenderable):
            console.line()
        console.print(
            (
                value
                if _safe_isinstance(value, RichRenderable)
                else Pretty(
                    value,
                    overflow=overflow,
                    indent_guides=indent_guides,
                    max_length=max_length,
                    max_string=max_string,
                    max_depth=max_depth,
                    expand_all=expand_all,
                    margin=12,
                )
            ),
            crop=crop,
            new_line_start=True,
            end="",
        )
    # strip trailing newline, not usually part of a text repr
    # I'm not sure if this should be prevented at a lower level
    return capture.get().rstrip("\n")


def _safe_isinstance(
    obj: object, class_or_tuple: Union[type, Tuple[type, ...]]
) -> bool:
    """isinstance can fail in rare cases, for example types with no __class__"""
    try:
        return isinstance(obj, class_or_tuple)
    except Exception:
        return False


def install(
    console: Optional["Console"] = None,
    overflow: "OverflowMethod" = "ignore",
    crop: bool = False,
    indent_guides: bool = False,
    max_length: Optional[int] = None,
    max_string: Optional[int] = None,
    max_depth: Optional[int] = None,
    expand_all: bool = False,
) -> None:
    """Install automatic pretty printing in the Python REPL.

    Args:
        console (Console, optional): Console instance or ``None`` to use global console. Defaults to None.
        overflow (Optional[OverflowMethod], optional): Overflow method. Defaults to "ignore".
        crop (Optional[bool], optional): Enable cropping of long lines. Defaults to False.
        indent_guides (bool, optional): Enable indentation guides. Defaults to False.
        max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to None.
        max_string (int, optional): Maximum length of string before truncating, or None to disable. Defaults to None.
        max_depth (int, optional): Maximum depth of nested data structures, or None for no maximum. Defaults to None.
        expand_all (bool, optional): Expand all containers. Defaults to False.
        max_frames (int): Maximum number of frames to show in a traceback, 0 for no maximum. Defaults to 100.
    """
    console = console or rich_module(M_CONSOLE).get_console()
    assert console is not None

    def display_hook(value: Any) -> None:
        """Replacement sys.displayhook which prettifies objects with Rich."""
        if value is not None:
            assert console is not None
            builtins._ = None  # type: ignore[attr-defined]
            console.print(
                (
                    value
                    if _safe_isinstance(value, RichRenderable)
                    else Pretty(
                        value,
                        overflow=overflow,
                        indent_guides=indent_guides,
                        max_length=max_length,
                        max_string=max_string,
                        max_depth=max_depth,
                        expand_all=expand_all,
                    )
                ),
                crop=crop,
            )
            builtins._ = value  # type: ignore[attr-defined]

    try:
        ip = get_ipython()  # type: ignore[name-defined]
    except NameError:
        sys.displayhook = display_hook
    else:
        from IPython.core.formatters import BaseFormatter

        def _rich_formatter_call(self, value: Any) -> Any:
            if self.pprint:
                return _ipy_display_hook(
                    value,
                    console=console,
                    overflow=overflow,
                    indent_guides=indent_guides,
                    max_length=max_length,
                    max_string=max_string,
                    max_depth=max_depth,
                    expand_all=expand_all,
                )
            return repr(value)

        RichFormatter = type(
            "RichFormatter",
            (BaseFormatter,),
            {"pprint": True, "__call__": _rich_formatter_call},
        )

        # replace plain text formatter with rich formatter
        rich_formatter = RichFormatter()
        ip.display_formatter.formatters["text/plain"] = rich_formatter


class Pretty:
    """A rich renderable that pretty prints an object.

    Args:
        _object (Any): An object to pretty print.
        highlighter (HighlighterType, optional): Highlighter object to apply to result, or None for ReprHighlighter. Defaults to None.
        indent_size (int, optional): Number of spaces in indent. Defaults to 4.
        justify (JustifyMethod, optional): Justify method, or None for default. Defaults to None.
        overflow (OverflowMethod, optional): Overflow method, or None for default. Defaults to None.
        no_wrap (Optional[bool], optional): Disable word wrapping. Defaults to False.
        indent_guides (bool, optional): Enable indentation guides. Defaults to False.
        max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to None.
        max_string (int, optional): Maximum length of string before truncating, or None to disable. Defaults to None.
        max_depth (int, optional): Maximum depth of nested data structures, or None for no maximum. Defaults to None.
        expand_all (bool, optional): Expand all containers. Defaults to False.
        margin (int, optional): Subtrace a margin from width to force containers to expand earlier. Defaults to 0.
        insert_line (bool, optional): Insert a new line if the output has multiple new lines. Defaults to False.
    """

    def __init__(
        self,
        _object: Any,
        highlighter: Optional["HighlighterType"] = None,
        *,
        indent_size: int = 4,
        justify: Optional["JustifyMethod"] = None,
        overflow: Optional["OverflowMethod"] = None,
        no_wrap: Optional[bool] = False,
        indent_guides: bool = False,
        max_length: Optional[int] = None,
        max_string: Optional[int] = None,
        max_depth: Optional[int] = None,
        expand_all: bool = False,
        margin: int = 0,
        insert_line: bool = False,
    ) -> None:
        self._object = _object
        self.highlighter = highlighter or _default_repr_highlighter()
        self.indent_size = indent_size
        self.justify: Optional["JustifyMethod"] = justify
        self.overflow: Optional["OverflowMethod"] = overflow
        self.no_wrap = no_wrap
        self.indent_guides = indent_guides
        self.max_length = max_length
        self.max_string = max_string
        self.max_depth = max_depth
        self.expand_all = expand_all
        self.margin = margin
        self.insert_line = insert_line

    def _repr_mimebundle_(
        self,
        include: Sequence[str],
        exclude: Sequence[str],
        **kwargs: Any,
    ):
        return rich_module(M_CONSOLE_WRITE).render_mimebundle(
            self, include, exclude, **kwargs
        )

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        pretty_str = pretty_repr(
            self._object,
            max_width=options.max_width - self.margin,
            indent_size=self.indent_size,
            max_length=self.max_length,
            max_string=self.max_string,
            max_depth=self.max_depth,
            expand_all=self.expand_all,
        )
        Text = rich_module(M_TEXT).Text
        pretty_text = Text.from_ansi(
            pretty_str,
            justify=self.justify or options.justify,
            overflow=self.overflow or options.overflow,
            no_wrap=pick_bool(self.no_wrap, options.no_wrap),
            style="pretty",
        )
        pretty_text = (
            self.highlighter(pretty_text)
            if pretty_text
            else Text(
                f"{type(self._object)}.__repr__ returned empty string",
                style="dim italic",
            )
        )
        if self.indent_guides and not options.ascii_only:
            pretty_text = pretty_text.with_indent_guides(
                self.indent_size, style="repr.indent"
            )
        if self.insert_line and "\n" in pretty_text:
            yield ""
        yield pretty_text

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        pretty_str = pretty_repr(
            self._object,
            max_width=options.max_width,
            indent_size=self.indent_size,
            max_length=self.max_length,
            max_string=self.max_string,
            max_depth=self.max_depth,
            expand_all=self.expand_all,
        )
        text_width = (
            max(cell_len(line) for line in pretty_str.splitlines()) if pretty_str else 0
        )
        return rich_module(M_MEASURE).Measurement(text_width, text_width)


def _get_braces_for_defaultdict(_object: DefaultDict[Any, Any]) -> Tuple[str, str, str]:
    return (
        f"defaultdict({_object.default_factory!r}, {{",
        "})",
        f"defaultdict({_object.default_factory!r}, {{}})",
    )


def _get_braces_for_deque(_object: Deque[Any]) -> Tuple[str, str, str]:
    if _object.maxlen is None:
        return ("deque([", "])", "deque()")
    return (
        "deque([",
        f"], maxlen={_object.maxlen})",
        f"deque(maxlen={_object.maxlen})",
    )


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


def is_expandable(obj: Any) -> bool:
    """Check if an object may be expanded by pretty print."""
    return (
        _safe_isinstance(obj, _CONTAINERS)
        or (is_dataclass(obj))
        or (hasattr(obj, "__rich_repr__"))
        or _is_attr_object(obj)
    ) and not isclass(obj)


def _node_init(
    self,
    key_repr: str = "",
    value_repr: str = "",
    open_brace: str = "",
    close_brace: str = "",
    empty: str = "",
    last: bool = False,
    is_tuple: bool = False,
    is_namedtuple: bool = False,
    children: Optional[List["Node"]] = None,
    key_separator: str = ": ",
    separator: str = ", ",
) -> None:
    self.key_repr = key_repr
    self.value_repr = value_repr
    self.open_brace = open_brace
    self.close_brace = close_brace
    self.empty = empty
    self.last = last
    self.is_tuple = is_tuple
    self.is_namedtuple = is_namedtuple
    self.children = children
    self.key_separator = key_separator
    self.separator = separator


def _node_iter_child_tokens(node: "Node") -> Iterable[str]:
    """Yield tokens for a node's children container."""
    if not node.children:
        yield node.empty
        return
    yield node.open_brace
    if node.is_tuple and not node.is_namedtuple and len(node.children) == 1:
        yield from node.children[0].iter_tokens()
        yield ","
        yield node.close_brace
        return
    for child in node.children:
        yield from child.iter_tokens()
        if not child.last:
            yield node.separator
    yield node.close_brace


def _node_iter_tokens(self) -> Iterable[str]:
    """Generate tokens for this node."""
    if self.key_repr:
        yield self.key_repr
        yield self.key_separator
    if self.value_repr:
        yield self.value_repr
    elif self.children is not None:
        yield from _node_iter_child_tokens(self)


def _node_check_length(self, start_length: int, max_length: int) -> bool:
    """Check the length fits within a limit."""
    total_length = start_length
    for token in self.iter_tokens():
        total_length += cell_len(token)
        if total_length > max_length:
            return False
    return True


def _node_str(self) -> str:
    return "".join(self.iter_tokens())


def _node_render(
    self, max_width: int = 80, indent_size: int = 4, expand_all: bool = False
) -> str:
    """Render the node to a pretty repr."""
    lines = [_Line(node=self, is_root=True)]
    line_no = 0
    while line_no < len(lines):
        line = lines[line_no]
        if line.expandable and not line.expanded:
            if expand_all or not line.check_length(max_width):
                lines[line_no : line_no + 1] = line.expand(indent_size)
        line_no += 1
    return "\n".join(str(line) for line in lines)


Node = type(
    "Node",
    (),
    {
        "__doc__": "A node in a repr tree. May be atomic or a container.",
        "__init__": _node_init,
        "iter_tokens": _node_iter_tokens,
        "check_length": _node_check_length,
        "__str__": _node_str,
        "render": _node_render,
    },
)


def _line_init(
    self,
    parent: Optional["_Line"] = None,
    is_root: bool = False,
    node: Optional[Node] = None,
    text: str = "",
    suffix: str = "",
    whitespace: str = "",
    expanded: bool = False,
    last: bool = False,
) -> None:
    self.parent = parent
    self.is_root = is_root
    self.node = node
    self.text = text
    self.suffix = suffix
    self.whitespace = whitespace
    self.expanded = expanded
    self.last = last


def _line_expandable(self) -> bool:
    """Check if the line may be expanded."""
    return bool(self.node is not None and self.node.children)


def _line_check_length(self, max_length: int) -> bool:
    """Check this line fits within a given number of cells."""
    start_length = len(self.whitespace) + cell_len(self.text) + cell_len(self.suffix)
    assert self.node is not None
    return self.node.check_length(start_length, max_length)


def _line_expand(self, indent_size: int) -> Iterable["_Line"]:
    """Expand this line by adding children on their own line."""
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
        yield _Line(
            parent=new_line,
            node=child,
            whitespace=child_whitespace,
            suffix=separator,
            last=last and not tuple_of_one,
        )
    yield _Line(
        text=node.close_brace,
        whitespace=whitespace,
        suffix=self.suffix,
        last=self.last,
    )


def _line_str(self) -> str:
    if self.last:
        return f"{self.whitespace}{self.text}{self.node or ''}"
    return f"{self.whitespace}{self.text}{self.node or ''}{self.suffix.rstrip()}"


_Line = type(
    "_Line",
    (),
    {
        "__doc__": "A line in repr output.",
        "__init__": _line_init,
        "expandable": property(_line_expandable),
        "check_length": _line_check_length,
        "expand": _line_expand,
        "__str__": _line_str,
    },
)


def _is_namedtuple(obj: Any) -> bool:
    """Checks if an object is most likely a namedtuple. It is possible
    to craft an object that passes this check and isn't a namedtuple, but
    there is only a minuscule chance of this happening unintentionally.

    Args:
        obj (Any): The object to test

    Returns:
        bool: True if the object is a namedtuple. False otherwise.
    """
    try:
        fields = getattr(obj, "_fields", None)
    except Exception:
        # Being very defensive - if we cannot get the attr then its not a namedtuple
        return False
    return isinstance(obj, tuple) and isinstance(fields, tuple)


def _traverse_to_repr(obj: Any, max_string: Optional[int]) -> str:
    """Get repr string for an object, but catch errors."""
    if (
        max_string is not None
        and _safe_isinstance(obj, (bytes, str))
        and len(obj) > max_string
    ):
        truncated = len(obj) - max_string
        return f"{obj[:max_string]!r}+{truncated}"
    try:
        return repr(obj)
    except Exception as error:
        return f"<repr-error {str(error)!r}>"


def _traverse_iter_rich_args(
    rich_args: Any,
) -> Iterable[Union[Any, Tuple[str, Any]]]:
    for arg in rich_args:
        if not _safe_isinstance(arg, tuple):
            yield arg
            continue
        if len(arg) == 3:
            key, child, default = arg
            if default != child:
                yield key, child
        elif len(arg) == 2:
            key, child = arg
            yield key, child
        elif len(arg) == 1:
            yield arg[0]


def _traverse_iter_attr_fields(
    obj: Any, attr_fields: Sequence["_attr_module.Attribute[Any]"]
) -> Iterable[Tuple[str, Any, Optional[Callable[[Any], str]]]]:
    """Iterate over attr fields and values."""
    for attr in attr_fields:
        if not attr.repr:
            continue
        try:
            value = getattr(obj, attr.name)
        except Exception as error:
            yield (attr.name, error, None)
        else:
            yield (attr.name, value, attr.repr if callable(attr.repr) else None)


_TraverseFn = Callable[..., "Node"]


def _traverse_rich_repr_children(
    traverse: _TraverseFn, args: List[Union[Any, Tuple[str, Any]]], depth: int
) -> List[Node]:
    children: List[Node] = []
    for last, arg in loop_last(args):
        if _safe_isinstance(arg, tuple):
            key, child = arg
            child_node = traverse(child, depth=depth + 1)
            child_node.last = last
            child_node.key_repr = key
            child_node.key_separator = "="
            children.append(child_node)
        else:
            child_node = traverse(arg, depth=depth + 1)
            child_node.last = last
            children.append(child_node)
    return children


def _traverse_rich_repr_node(
    traverse: _TraverseFn,
    obj: Any,
    obj_id: int,
    root: bool,
    depth: int,
    reached_max_depth: bool,
    rich_repr_result: RichReprResult,
    visited_ids: Set[int],
) -> Node:
    visited_ids.add(obj_id)
    angular = getattr(obj.__rich_repr__, "angular", False)
    args = list(_traverse_iter_rich_args(rich_repr_result))
    class_name = obj.__class__.__name__
    if not args:
        node = Node(
            value_repr=f"<{class_name}>" if angular else f"{class_name}()",
            children=[],
            last=root,
        )
        visited_ids.remove(obj_id)
        return node
    if reached_max_depth:
        node = Node(
            value_repr=f"<{class_name}...>" if angular else f"{class_name}(...)"
        )
        visited_ids.remove(obj_id)
        return node
    children = _traverse_rich_repr_children(traverse, args, depth)
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
    visited_ids.remove(obj_id)
    return node


def _traverse_attr_node(
    traverse: _TraverseFn,
    obj: Any,
    obj_id: int,
    root: bool,
    depth: int,
    reached_max_depth: bool,
    visited_ids: Set[int],
) -> Node:
    visited_ids.add(obj_id)
    children: List[Node] = []
    attr_fields = _get_attr_fields(obj)
    if not attr_fields:
        node = Node(value_repr=f"{obj.__class__.__name__}()", children=[], last=root)
        visited_ids.remove(obj_id)
        return node
    if reached_max_depth:
        node = Node(value_repr=f"{obj.__class__.__name__}(...)")
        visited_ids.remove(obj_id)
        return node
    node = Node(
        open_brace=f"{obj.__class__.__name__}(",
        close_brace=")",
        children=children,
        last=root,
    )
    for last, (name, value, repr_callable) in loop_last(
        _traverse_iter_attr_fields(obj, attr_fields)
    ):
        if repr_callable:
            child_node = Node(value_repr=str(repr_callable(value)))
        else:
            child_node = traverse(value, depth=depth + 1)
        child_node.last = last
        child_node.key_repr = name
        child_node.key_separator = "="
        children.append(child_node)
    visited_ids.remove(obj_id)
    return node


def _traverse_dataclass_node(
    traverse: _TraverseFn,
    obj: Any,
    obj_id: int,
    root: bool,
    depth: int,
    reached_max_depth: bool,
    visited_ids: Set[int],
) -> Node:
    visited_ids.add(obj_id)
    children: List[Node] = []
    if reached_max_depth:
        node = Node(value_repr=f"{obj.__class__.__name__}(...)")
        visited_ids.remove(obj_id)
        return node
    node = Node(
        open_brace=f"{obj.__class__.__name__}(",
        close_brace=")",
        children=children,
        last=root,
        empty=f"{obj.__class__.__name__}()",
    )
    for last, field in loop_last(
        field for field in fields(obj) if field.repr and hasattr(obj, field.name)
    ):
        child_node = traverse(getattr(obj, field.name), depth=depth + 1)
        child_node.key_repr = field.name
        child_node.last = last
        child_node.key_separator = "="
        children.append(child_node)
    visited_ids.remove(obj_id)
    return node


def _traverse_namedtuple_node(
    traverse: _TraverseFn,
    obj: Any,
    obj_id: int,
    depth: int,
    reached_max_depth: bool,
    visited_ids: Set[int],
) -> Node:
    visited_ids.add(obj_id)
    class_name = obj.__class__.__name__
    if reached_max_depth:
        node = Node(value_repr=f"{class_name}(...)")
        visited_ids.remove(obj_id)
        return node
    children: List[Node] = []
    node = Node(
        open_brace=f"{class_name}(",
        close_brace=")",
        children=children,
        empty=f"{class_name}()",
    )
    for last, (key, value) in loop_last(obj._asdict().items()):
        child_node = traverse(value, depth=depth + 1)
        child_node.key_repr = key
        child_node.last = last
        child_node.key_separator = "="
        children.append(child_node)
    visited_ids.remove(obj_id)
    return node


def _traverse_container_children(
    traverse: _TraverseFn,
    obj: Any,
    depth: int,
    max_length: Optional[int],
    max_string: Optional[int],
) -> List[Node]:
    children: List[Node] = []
    num_items = len(obj)
    last_item_index = num_items - 1
    if _safe_isinstance(obj, _MAPPING_CONTAINERS):
        iter_items = iter(obj.items())
        if max_length is not None:
            iter_items = islice(iter_items, max_length)
        for index, (key, child) in enumerate(iter_items):
            child_node = traverse(child, depth=depth + 1)
            child_node.key_repr = _traverse_to_repr(key, max_string)
            child_node.last = index == last_item_index
            children.append(child_node)
    else:
        iter_values = iter(obj)
        if max_length is not None:
            iter_values = islice(iter_values, max_length)
        for index, child in enumerate(iter_values):
            child_node = traverse(child, depth=depth + 1)
            child_node.last = index == last_item_index
            children.append(child_node)
    if max_length is not None and num_items > max_length:
        children.append(Node(value_repr=f"... +{num_items - max_length}", last=True))
    return children


def _traverse_container_node(
    traverse: _TraverseFn,
    obj: Any,
    obj_id: int,
    obj_type: type,
    root: bool,
    depth: int,
    reached_max_depth: bool,
    max_length: Optional[int],
    max_string: Optional[int],
    visited_ids: Set[int],
) -> Node:
    visited_ids.add(obj_id)
    open_brace, close_brace, empty = _BRACES[obj_type](obj)
    if reached_max_depth:
        node = Node(value_repr=f"{open_brace}...{close_brace}")
        visited_ids.remove(obj_id)
        return node
    if obj_type.__repr__ != type(obj).__repr__:
        node = Node(value_repr=_traverse_to_repr(obj, max_string), last=root)
        visited_ids.remove(obj_id)
        return node
    if not obj:
        node = Node(empty=empty, children=[], last=root)
        visited_ids.remove(obj_id)
        return node
    children = _traverse_container_children(
        traverse, obj, depth, max_length, max_string
    )
    node = Node(
        open_brace=open_brace,
        close_brace=close_brace,
        children=children,
        last=root,
    )
    visited_ids.remove(obj_id)
    return node


def traverse(
    _object: Any,
    max_length: Optional[int] = None,
    max_string: Optional[int] = None,
    max_depth: Optional[int] = None,
) -> Node:
    """Traverse object and generate a tree.

    Args:
        _object (Any): Object to be traversed.
        max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to None.
        max_string (int, optional): Maximum length of string before truncating, or None to disable truncating.
            Defaults to None.
        max_depth (int, optional): Maximum depth of data structures, or None for no maximum.
            Defaults to None.

    Returns:
        Node: The root of a tree structure which can be used to render a pretty repr.
    """

    visited_ids: Set[int] = set()

    def _traverse(obj: Any, root: bool = False, depth: int = 0) -> Node:
        """Walk the object depth first."""
        obj_id = id(obj)
        if obj_id in visited_ids:
            return Node(value_repr="...")

        reached_max_depth = max_depth is not None and depth >= max_depth
        try:
            fake_attributes = hasattr(
                obj, "awehoi234_wdfjwljet234_234wdfoijsdfmmnxpi492"
            )
        except Exception:
            fake_attributes = False

        rich_repr_result: Optional[RichReprResult] = None
        if not fake_attributes:
            try:
                if hasattr(obj, "__rich_repr__") and not isclass(obj):
                    rich_repr_result = obj.__rich_repr__()
            except Exception:
                pass

        if rich_repr_result is not None:
            node = _traverse_rich_repr_node(
                _traverse,
                obj,
                obj_id,
                root,
                depth,
                reached_max_depth,
                rich_repr_result,
                visited_ids,
            )
        elif _is_attr_object(obj) and not fake_attributes:
            node = _traverse_attr_node(
                _traverse, obj, obj_id, root, depth, reached_max_depth, visited_ids
            )
        elif (
            is_dataclass(obj)
            and not _safe_isinstance(obj, type)
            and not fake_attributes
            and _is_dataclass_repr(obj)
        ):
            node = _traverse_dataclass_node(
                _traverse, obj, obj_id, root, depth, reached_max_depth, visited_ids
            )
        elif _is_namedtuple(obj) and _has_default_namedtuple_repr(obj):
            node = _traverse_namedtuple_node(
                _traverse, obj, obj_id, depth, reached_max_depth, visited_ids
            )
        elif _safe_isinstance(obj, _CONTAINERS):
            obj_type = next(
                container_type
                for container_type in _CONTAINERS
                if _safe_isinstance(obj, container_type)
            )
            node = _traverse_container_node(
                _traverse,
                obj,
                obj_id,
                obj_type,
                root,
                depth,
                reached_max_depth,
                max_length,
                max_string,
                visited_ids,
            )
        else:
            node = Node(value_repr=_traverse_to_repr(obj, max_string), last=root)
        node.is_tuple = type(obj) == tuple
        node.is_namedtuple = _is_namedtuple(obj)
        return node

    node = _traverse(_object, root=True)
    return node


def pretty_repr(
    _object: Any,
    *,
    max_width: int = 80,
    indent_size: int = 4,
    max_length: Optional[int] = None,
    max_string: Optional[int] = None,
    max_depth: Optional[int] = None,
    expand_all: bool = False,
) -> str:
    """Prettify repr string by expanding on to new lines to fit within a given width.

    Args:
        _object (Any): Object to repr.
        max_width (int, optional): Desired maximum width of repr string. Defaults to 80.
        indent_size (int, optional): Number of spaces to indent. Defaults to 4.
        max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to None.
        max_string (int, optional): Maximum length of string before truncating, or None to disable truncating.
            Defaults to None.
        max_depth (int, optional): Maximum depth of nested data structure, or None for no depth.
            Defaults to None.
        expand_all (bool, optional): Expand all containers regardless of available width. Defaults to False.

    Returns:
        str: A possibly multi-line representation of the object.
    """

    if _safe_isinstance(_object, Node):
        node = _object
    else:
        node = traverse(
            _object, max_length=max_length, max_string=max_string, max_depth=max_depth
        )
    repr_str: str = node.render(
        max_width=max_width, indent_size=indent_size, expand_all=expand_all
    )
    return repr_str


def pprint(
    _object: Any,
    *,
    console: Optional["Console"] = None,
    indent_guides: bool = True,
    max_length: Optional[int] = None,
    max_string: Optional[int] = None,
    max_depth: Optional[int] = None,
    expand_all: bool = False,
) -> None:
    """A convenience function for pretty printing.

    Args:
        _object (Any): Object to pretty print.
        console (Console, optional): Console instance, or None to use default. Defaults to None.
        max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to None.
        max_string (int, optional): Maximum length of strings before truncating, or None to disable. Defaults to None.
        max_depth (int, optional): Maximum depth for nested data structures, or None for unlimited depth. Defaults to None.
        indent_guides (bool, optional): Enable indentation guides. Defaults to True.
        expand_all (bool, optional): Expand all containers. Defaults to False.
    """
    _console = (
        rich_module(M_CONSOLE).get_console() if console is None else console
    )
    _console.print(
        Pretty(
            _object,
            max_length=max_length,
            max_string=max_string,
            max_depth=max_depth,
            indent_guides=indent_guides,
            expand_all=expand_all,
            overflow="ignore",
        ),
        soft_wrap=True,
    )


if __name__ == "__main__":  # pragma: no cover

    def _broken_repr(self) -> str:
        1 / 0
        return "this will fail"

    BrokenRepr = type("BrokenRepr", (), {"__repr__": _broken_repr})

    from typing import NamedTuple

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

    d = defaultdict(int)
    d["foo"] = 5
    data = {
        "foo": [
            1,
            "Hello World!",
            100.123,
            323.232,
            432324.0,
            {5, 6, 7, (1, 2, 3, 4), 8},
        ],
        "bar": frozenset({1, 2, 3}),
        "defaultdict": defaultdict(
            list, {"crumble": ["apple", "rhubarb", "butter", "sugar", "flour"]}
        ),
        "counter": Counter(
            [
                "apple",
                "orange",
                "pear",
                "kumquat",
                "kumquat",
                "durian" * 100,
            ]
        ),
        "atomic": (False, True, None),
        "namedtuple": StockKeepingUnit(
            "Sparkling British Spring Water",
            "Carbonated spring water",
            0.9,
            "water",
            ["its amazing!", "its terrible!"],
        ),
        "Broken": BrokenRepr(),
    }
    data["foo"].append(data)  # type: ignore[attr-defined]

    from . import print

    print(Pretty(data, indent_guides=True, max_string=20))

    Thing = type(
        "Thing",
        (),
        {"__repr__": lambda self: "Hello\x1b[38;5;239m World!"},
    )

    print(Pretty(Thing()))
