import builtins
import collections
import dataclasses
import inspect
import os
import reprlib
import sys
from array import array
from collections import Counter, UserDict, UserList, defaultdict, deque
from dataclasses import dataclass, fields, is_dataclass
from inspect import isclass
from itertools import islice
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, DefaultDict, Deque, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union
from .repr import RichReprResult
try:
    import attr as _attr_module
    _has_attrs = hasattr(_attr_module, 'ib')
except ImportError:
    _has_attrs = False
from ._loop import loop_last
from ._pick import pick_bool
from .cells import cell_len
from .text import Text
from ._jupyter_mixin import JupyterMixin
from ._pretty_common import (
    Node,
    _BRACES,
    _CONTAINERS,
    _MAPPING_CONTAINERS,
    _Line,
    _get_attr_fields,
    _has_default_namedtuple_repr,
    _is_attr_object,
    _is_dataclass_repr,
    _is_namedtuple,
    _iter_attr_field_values,
    _iter_rich_repr_args,
    _safe_isinstance,
)

def _ipy_display_hook(value: Any, console: Optional['Console']=None, overflow: 'OverflowMethod'='ignore', crop: bool=False, indent_guides: bool=False, max_length: Optional[int]=None, max_string: Optional[int]=None, max_depth: Optional[int]=None, expand_all: bool=False) -> Union[str, None]:
    from ._runtime import get_console_renderable, get_global_console

    ConsoleRenderable = get_console_renderable()
    if value is None or type(value).__name__ == "JupyterRenderable":
        return None

    console = console or get_global_console()
    with console.capture() as capture:
        if _safe_isinstance(value, ConsoleRenderable):
            console.line()
        console.print(value if _is_rich_renderable(value) else Pretty(value, overflow=overflow, indent_guides=indent_guides, max_length=max_length, max_string=max_string, max_depth=max_depth, expand_all=expand_all, margin=12), crop=crop, new_line_start=True, end='')
    return capture.get().rstrip('\n')

def _is_rich_renderable(obj: object) -> bool:
    """Return True if *obj* supports the Rich render protocol."""
    return hasattr(obj, '__rich_console__') or hasattr(obj, '__rich__')

def install(console: Optional['Console']=None, overflow: 'OverflowMethod'='ignore', crop: bool=False, indent_guides: bool=False, max_length: Optional[int]=None, max_string: Optional[int]=None, max_depth: Optional[int]=None, expand_all: bool=False) -> None:
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
    from ._runtime import get_global_console

    console = console or get_global_console()
    assert console is not None

    def display_hook(value: Any) -> None:
        """Replacement sys.displayhook which prettifies objects with Rich."""
        if value is not None:
            assert console is not None
            builtins._ = None
            console.print(value if _is_rich_renderable(value) else Pretty(value, overflow=overflow, indent_guides=indent_guides, max_length=max_length, max_string=max_string, max_depth=max_depth, expand_all=expand_all), crop=crop)
            builtins._ = value
    try:
        ip = get_ipython()
    except NameError:
        sys.displayhook = display_hook
    else:
        from IPython.core.formatters import BaseFormatter

        class RichFormatter(BaseFormatter):
            pprint: bool = True

            def __call__(self, value: Any) -> Any:
                if self.pprint:
                    return _ipy_display_hook(value, console=console, overflow=overflow, indent_guides=indent_guides, max_length=max_length, max_string=max_string, max_depth=max_depth, expand_all=expand_all)
                else:
                    return repr(value)
        rich_formatter = RichFormatter()
        ip.display_formatter.formatters['text/plain'] = rich_formatter

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


    def __init__(self, _object: Any, highlighter: Optional['HighlighterType']=None, *, indent_size: int=4, justify: Optional['JustifyMethod']=None, overflow: Optional['OverflowMethod']=None, no_wrap: Optional[bool]=False, indent_guides: bool=False, max_length: Optional[int]=None, max_string: Optional[int]=None, max_depth: Optional[int]=None, expand_all: bool=False, margin: int=0, insert_line: bool=False) -> None:
        self._object = _object
        if highlighter is None:
            from ._runtime import _mod

            highlighter = _mod("rich.highlighter").ReprHighlighter()
        self.highlighter = highlighter
        self.indent_size = indent_size
        self.justify: Optional['JustifyMethod'] = justify
        self.overflow: Optional['OverflowMethod'] = overflow
        self.no_wrap = no_wrap
        self.indent_guides = indent_guides
        self.max_length = max_length
        self.max_string = max_string
        self.max_depth = max_depth
        self.expand_all = expand_all
        self.margin = margin
        self.insert_line = insert_line

    def __rich_console__(self, console: 'Console', options: 'ConsoleOptions') -> 'RenderResult':
        pretty_str = pretty_repr(self._object, max_width=options.max_width - self.margin, indent_size=self.indent_size, max_length=self.max_length, max_string=self.max_string, max_depth=self.max_depth, expand_all=self.expand_all)
        pretty_text = Text.from_ansi(pretty_str, justify=self.justify or options.justify, overflow=self.overflow or options.overflow, no_wrap=pick_bool(self.no_wrap, options.no_wrap), style='pretty')
        pretty_text = self.highlighter(pretty_text) if pretty_text else Text(f'{type(self._object)}.__repr__ returned empty string', style='dim italic')
        if self.indent_guides and (not options.ascii_only):
            pretty_text = pretty_text.with_indent_guides(self.indent_size, style='repr.indent')
        if self.insert_line and '\n' in pretty_text:
            yield ''
        yield pretty_text

    def __rich_measure__(self, console: 'Console', options: 'ConsoleOptions'):
        from .measure import Measurement
        pretty_str = pretty_repr(self._object, max_width=options.max_width, indent_size=self.indent_size, max_length=self.max_length, max_string=self.max_string, max_depth=self.max_depth, expand_all=self.expand_all)
        text_width = max((cell_len(line) for line in pretty_str.splitlines())) if pretty_str else 0
        return Measurement(text_width, text_width)

def is_expandable(obj: Any) -> bool:
    """Check if an object may be expanded by pretty print."""
    return (_safe_isinstance(obj, _CONTAINERS) or is_dataclass(obj) or hasattr(obj, '__rich_repr__') or _is_attr_object(obj)) and (not isclass(obj))

def traverse(_object: Any, max_length: Optional[int]=None, max_string: Optional[int]=None, max_depth: Optional[int]=None) -> Node:
    """Traverse object and generate a tree."""
    from ._pretty_traverse import traverse_object
    return traverse_object(_object, max_length, max_string, max_depth)

def pretty_repr(_object: Any, *, max_width: int=80, indent_size: int=4, max_length: Optional[int]=None, max_string: Optional[int]=None, max_depth: Optional[int]=None, expand_all: bool=False) -> str:
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
        node = traverse(_object, max_length=max_length, max_string=max_string, max_depth=max_depth)
    repr_str: str = node.render(max_width=max_width, indent_size=indent_size, expand_all=expand_all)
    return repr_str

def pprint(_object: Any, *, console: Optional['Console']=None, indent_guides: bool=True, max_length: Optional[int]=None, max_string: Optional[int]=None, max_depth: Optional[int]=None, expand_all: bool=False) -> None:
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
    from ._runtime import get_global_console

    _console = get_global_console() if console is None else console
    _console.print(Pretty(_object, max_length=max_length, max_string=max_string, max_depth=max_depth, indent_guides=indent_guides, expand_all=expand_all, overflow='ignore'), soft_wrap=True)


from ._pretty_bridge import register_pretty_module

register_pretty_module(sys.modules[__name__])