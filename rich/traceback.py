from __future__ import annotations

from ._lazy import import_attr
import inspect
import linecache
import os
import sys
from dataclasses import dataclass, field
from itertools import islice
from traceback import walk_tb
from types import ModuleType, TracebackType
from importlib import import_module
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from pygments.lexers import guess_lexer_for_filename
from pygments.token import Comment, Keyword, Name, Number, Operator, String
from pygments.token import Text as TextToken
from pygments.token import Token
from pygments.util import ClassNotFound

loop_first_last = import_attr('rich._loop', 'loop_first_last')
loop_last = import_attr('rich._loop', 'loop_last')
Columns = import_attr('rich.columns', 'Columns')
Console = import_attr('rich.console', 'Console')
ConsoleOptions = import_attr('rich.console', 'ConsoleOptions')
ConsoleRenderable = import_attr('rich.console', 'ConsoleRenderable')
OverflowMethod = import_attr('rich.console', 'OverflowMethod')
Group = import_attr('rich.console', 'Group')
RenderResult = import_attr('rich.console', 'RenderResult')
group = import_attr('rich.console', 'group')
Constrain = import_attr('rich.constrain', 'Constrain')
RegexHighlighter = import_attr('rich.highlighter', 'RegexHighlighter')
ReprHighlighter = import_attr('rich.highlighter', 'ReprHighlighter')
Panel = import_attr('rich.panel', 'Panel')
render_scope = import_attr('rich.scope', 'render_scope')
Style = import_attr('rich.style', 'Style')
Syntax = import_attr('rich.syntax', 'Syntax')
SyntaxPosition = import_attr('rich.syntax', 'SyntaxPosition')
Text = import_attr('rich.text', 'Text')
Theme = import_attr('rich.theme', 'Theme')

WINDOWS = sys.platform == "win32"

LOCALS_MAX_LENGTH = 10
LOCALS_MAX_STRING = 80


def _iter_syntax_lines_single(line: int, column1: int, column2: int) -> Iterable[Tuple[int, int, int]]:
    yield line, column1, column2


def _iter_syntax_lines_range(
    line1: int, line2: int, column1: int, column2: int
) -> Iterable[Tuple[int, int, int]]:
    yield line1, column1, -1
    for _first, last, line_no in loop_first_last(range(line1 + 1, line2)):
        if last:
            yield line_no, 0, column2
        else:
            yield line_no, 0, -1


def _iter_syntax_lines(
    start: SyntaxPosition, end: SyntaxPosition
) -> Iterable[Tuple[int, int, int]]:
    """Yield start and end positions per line.

    Args:
        start: Start position.
        end: End position.

    Returns:
        Iterable of (LINE, COLUMN1, COLUMN2).
    """

    line1, column1 = start
    line2, column2 = end

    if line1 == line2:
        yield from _iter_syntax_lines_single(line1, column1, column2)
    else:
        yield from _iter_syntax_lines_range(line1, line2, column1, column2)


def install(
    *,
    console: Optional[Console] = None,
    width: Optional[int] = 100,
    code_width: Optional[int] = 88,
    extra_lines: int = 3,
    theme: Optional[str] = None,
    word_wrap: bool = False,
    show_locals: bool = False,
    locals_max_length: int = LOCALS_MAX_LENGTH,
    locals_max_string: int = LOCALS_MAX_STRING,
    locals_max_depth: Optional[int] = None,
    locals_hide_dunder: bool = True,
    locals_hide_sunder: Optional[bool] = None,
    locals_overflow: Optional[OverflowMethod] = None,
    indent_guides: bool = True,
    suppress: Iterable[Union[str, ModuleType]] = (),
    max_frames: int = 100,
) -> Callable[[Type[BaseException], BaseException, Optional[TracebackType]], Any]:
    """Install a rich traceback handler.

    Once installed, any tracebacks will be printed with syntax highlighting and rich formatting.


    Args:
        console (Optional[Console], optional): Console to write exception to. Default uses internal Console instance.
        width (Optional[int], optional): Width (in characters) of traceback. Defaults to 100.
        code_width (Optional[int], optional): Code width (in characters) of traceback. Defaults to 88.
        extra_lines (int, optional): Extra lines of code. Defaults to 3.
        theme (Optional[str], optional): Pygments theme to use in traceback. Defaults to ``None`` which will pick
            a theme appropriate for the platform.
        word_wrap (bool, optional): Enable word wrapping of long lines. Defaults to False.
        show_locals (bool, optional): Enable display of local variables. Defaults to False.
        locals_max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to 10.
        locals_max_string (int, optional): Maximum length of string before truncating, or None to disable. Defaults to 80.
        locals_max_depth (int, optional): Maximum depths of locals before truncating, or None to disable. Defaults to None.
        locals_hide_dunder (bool, optional): Hide locals prefixed with double underscore. Defaults to True.
        locals_hide_sunder (bool, optional): Hide locals prefixed with single underscore. Defaults to False.
        locals_overflow (OverflowMethod, optional): How to handle overflowing locals, or None to disable. Defaults to None.
        indent_guides (bool, optional): Enable indent guides in code and locals. Defaults to True.
        suppress (Sequence[Union[str, ModuleType]]): Optional sequence of modules or paths to exclude from traceback.

    Returns:
        Callable: The previous exception handler that was replaced.

    """
    traceback_console = Console(stderr=True) if console is None else console

    locals_hide_sunder = (
        True
        if (traceback_console.is_jupyter and locals_hide_sunder is None)
        else locals_hide_sunder
    )

    def excepthook(
        type_: Type[BaseException],
        value: BaseException,
        traceback: Optional[TracebackType],
    ) -> None:
        exception_traceback = Traceback.from_exception(
            type_,
            value,
            traceback,
            width=width,
            code_width=code_width,
            extra_lines=extra_lines,
            theme=theme,
            word_wrap=word_wrap,
            show_locals=show_locals,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            locals_max_depth=locals_max_depth,
            locals_hide_dunder=locals_hide_dunder,
            locals_hide_sunder=bool(locals_hide_sunder),
            locals_overflow=locals_overflow,
            indent_guides=indent_guides,
            suppress=suppress,
            max_frames=max_frames,
        )
        traceback_console.print(exception_traceback)

    def ipy_excepthook_closure(ip: Any) -> None:  # pragma: no cover
        tb_data = {}  # store information about showtraceback call
        default_showtraceback = ip.showtraceback  # keep reference of default traceback

        def ipy_show_traceback(*args: Any, **kwargs: Any) -> None:
            """wrap the default ip.showtraceback to store info for ip._showtraceback"""
            nonlocal tb_data
            tb_data = kwargs
            default_showtraceback(*args, **kwargs)

        def ipy_display_traceback(
            *args: Any, is_syntax: bool = False, **kwargs: Any
        ) -> None:
            """Internally called traceback from ip._showtraceback"""
            nonlocal tb_data
            exc_tuple = ip._get_exc_info()

            # do not display trace on syntax error
            tb: Optional[TracebackType] = None if is_syntax else exc_tuple[2]

            # determine correct tb_offset
            compiled = tb_data.get("running_compiled_code", False)
            tb_offset = tb_data.get("tb_offset")
            if tb_offset is None:
                tb_offset = 1 if compiled else 0
            # remove ipython internal frames from trace with tb_offset
            for _ in range(tb_offset):
                if tb is None:
                    break
                tb = tb.tb_next

            excepthook(exc_tuple[0], exc_tuple[1], tb)
            tb_data = {}  # clear data upon usage

        # replace _showtraceback instead of showtraceback to allow ipython features such as debugging to work
        # this is also what the ipython docs recommends to modify when subclassing InteractiveShell
        ip._showtraceback = ipy_display_traceback
        # add wrapper to capture tb_data
        ip.showtraceback = ipy_show_traceback
        ip.showsyntaxerror = lambda *args, **kwargs: ipy_display_traceback(
            *args, is_syntax=True, **kwargs
        )

    try:  # pragma: no cover
        # if within ipython, use customized traceback
        from IPython import get_ipython

        ip = get_ipython()
        ipy_excepthook_closure(ip)
        return sys.excepthook
    except Exception:
        # otherwise use default system hook
        old_excepthook = sys.excepthook
        sys.excepthook = excepthook
        return old_excepthook


@dataclass
class Frame:
    filename: str
    lineno: int
    name: str
    line: str = ""
    locals: Optional[Dict[str, Any]] = None
    last_instruction: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None


@dataclass
class _SyntaxError:
    offset: int
    filename: str
    line: str
    lineno: int
    msg: str
    notes: List[str] = field(default_factory=list)


@dataclass
class Stack:
    exc_type: str
    exc_value: str
    syntax_error: Optional[_SyntaxError] = None
    is_cause: bool = False
    frames: List[Frame] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    is_group: bool = False
    exceptions: List["Trace"] = field(default_factory=list)


@dataclass
class Trace:
    stacks: List[Stack]


def _traceback_safe_str(_object: Any) -> str:
    """Don't allow exceptions from __str__ to propagate."""
    try:
        return str(_object)
    except Exception:
        return "<exception str() failed>"


def _traceback_filter_locals(
    iter_locals: Iterable[Tuple[str, object]],
    *,
    locals_hide_dunder: bool,
    locals_hide_sunder: bool,
) -> Iterable[Tuple[str, object]]:
    if not (locals_hide_dunder or locals_hide_sunder):
        yield from iter_locals
        return
    for key, value in iter_locals:
        if locals_hide_dunder and key.startswith("__"):
            continue
        if locals_hide_sunder and key.startswith("_"):
            continue
        yield key, value


def _traceback_frame_last_instruction(
    frame_summary: Any,
) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
    if sys.version_info < (3, 11):
        return None
    instruction_index = frame_summary.f_lasti // 2
    instruction_position = next(
        islice(
            frame_summary.f_code.co_positions(),
            instruction_index,
            instruction_index + 1,
        )
    )
    start_line, end_line, start_column, end_column = instruction_position
    if (
        start_line is not None
        and end_line is not None
        and start_column is not None
        and end_column is not None
    ):
        return (start_line, start_column), (end_line, end_column)
    return None


def _traceback_resolve_filename(filename: str, import_cwd: str) -> str:
    if filename and not filename.startswith("<"):
        if not os.path.isabs(filename):
            filename = os.path.join(import_cwd, filename)
    return filename or "?"


def _traceback_build_frame(
    frame_summary: Any,
    line_no: int,
    *,
    import_cwd: str,
    show_locals: bool,
    locals_max_length: int,
    locals_max_string: int,
    locals_max_depth: Optional[int],
    locals_hide_dunder: bool,
    locals_hide_sunder: bool,
) -> Frame:
    filename = _traceback_resolve_filename(
        frame_summary.f_code.co_filename, import_cwd
    )
    locals: Optional[Dict[str, Any]] = None
    if show_locals:
        locals = {
            key: import_module("rich.pretty").traverse(
                value,
                max_length=locals_max_length,
                max_string=locals_max_string,
                max_depth=locals_max_depth,
            )
            for key, value in _traceback_filter_locals(
                frame_summary.f_locals.items(),
                locals_hide_dunder=locals_hide_dunder,
                locals_hide_sunder=locals_hide_sunder,
            )
            if not (inspect.isfunction(value) or inspect.isclass(value))
        }
    return Frame(
        filename=filename,
        lineno=line_no,
        name=frame_summary.f_code.co_name,
        locals=locals,
        last_instruction=_traceback_frame_last_instruction(frame_summary),
    )


def _traceback_append_exception_group(
    stack: Stack,
    exc_value: BaseException,
    grouped_exceptions: Set[BaseException],
    extract: Callable[..., Trace],
    *,
    show_locals: bool,
    locals_max_length: int,
    locals_max_string: int,
    locals_hide_dunder: bool,
    locals_hide_sunder: bool,
) -> None:
    if sys.version_info < (3, 11):
        return
    from builtins import BaseExceptionGroup, ExceptionGroup

    if not isinstance(exc_value, (BaseExceptionGroup, ExceptionGroup)):
        return
    stack.is_group = True
    for exception in exc_value.exceptions:
        if exception in grouped_exceptions:
            continue
        grouped_exceptions.add(exception)
        stack.exceptions.append(
            extract(
                type(exception),
                exception,
                exception.__traceback__,
                show_locals=show_locals,
                locals_max_length=locals_max_length,
                locals_hide_dunder=locals_hide_dunder,
                locals_hide_sunder=locals_hide_sunder,
                _visited_exceptions=grouped_exceptions,
            )
        )


def _traceback_set_syntax_error(
    stack: Stack, exc_value: BaseException, notes: List[str]
) -> None:
    if not isinstance(exc_value, SyntaxError):
        return
    stack.syntax_error = _SyntaxError(
        offset=exc_value.offset or 0,
        filename=exc_value.filename or "?",
        lineno=exc_value.lineno or 0,
        line=exc_value.text or "",
        msg=exc_value.msg,
        notes=notes,
    )


def _traceback_walk_stack_frames(
    stack: Stack,
    traceback: Optional[TracebackType],
    *,
    import_cwd: str,
    show_locals: bool,
    locals_max_length: int,
    locals_max_string: int,
    locals_max_depth: Optional[int],
    locals_hide_dunder: bool,
    locals_hide_sunder: bool,
) -> None:
    append = stack.frames.append
    for frame_summary, line_no in walk_tb(traceback):
        if frame_summary.f_locals.get("_rich_traceback_omit", False):
            continue
        frame = _traceback_build_frame(
            frame_summary,
            line_no,
            import_cwd=import_cwd,
            show_locals=show_locals,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            locals_max_depth=locals_max_depth,
            locals_hide_dunder=locals_hide_dunder,
            locals_hide_sunder=locals_hide_sunder,
        )
        append(frame)
        if frame_summary.f_locals.get("_rich_traceback_guard", False):
            del stack.frames[:]


def _traceback_next_linked_exception(
    exc_value: BaseException,
    grouped_exceptions: Set[BaseException],
) -> Optional[Tuple[Type[BaseException], BaseException, Optional[TracebackType], bool]]:
    if grouped_exceptions:
        return None
    cause = getattr(exc_value, "__cause__", None)
    if cause is not None and cause is not exc_value:
        return cause.__class__, cause, cause.__traceback__, True
    cause = exc_value.__context__
    if cause is not None and not getattr(exc_value, "__suppress_context__", False):
        return cause.__class__, cause, cause.__traceback__, False
    return None


def _traceback_render_locals(
    frame: Frame,
    *,
    indent_guides: bool,
    locals_max_length: int,
    locals_max_string: int,
    locals_max_depth: Optional[int],
    locals_overflow: Optional[OverflowMethod],
) -> Iterable[ConsoleRenderable]:
    if frame.locals:
        yield render_scope(
            frame.locals,
            title="locals",
            indent_guides=indent_guides,
            max_length=locals_max_length,
            max_string=locals_max_string,
            max_depth=locals_max_depth,
            overflow=locals_overflow,
        )


def _traceback_frame_header_text(
    frame: Frame,
    *,
    path_highlighter: "PathHighlighter",
    first: bool,
) -> Text:
    if os.path.exists(frame.filename):
        return Text.assemble(
            path_highlighter(Text(frame.filename, style="pygments.string")),
            (":", "pygments.text"),
            (str(frame.lineno), "pygments.number"),
            " in ",
            (frame.name, "pygments.function"),
            style="pygments.text",
        )
    return Text.assemble(
        "in ",
        (frame.name, "pygments.function"),
        (":", "pygments.text"),
        (str(frame.lineno), "pygments.number"),
        style="pygments.text",
    )


def _traceback_stylize_last_instruction(
    syntax: Syntax,
    frame: Frame,
    code_lines: List[str],
) -> None:
    if frame.last_instruction is None:
        return
    start, end = frame.last_instruction
    for line1, column1, column2 in _iter_syntax_lines(start, end):
        try:
            if column1 == 0:
                line = code_lines[line1 - 1]
                column1 = len(line) - len(line.lstrip())
            if column2 == -1:
                column2 = len(code_lines[line1 - 1])
        except IndexError:
            continue
        syntax.stylize_range(
            style="traceback.error_range",
            start=(line1, column1),
            end=(line1, column2),
        )


def _traceback_render_frame_code(
    frame: Frame,
    traceback: "Traceback",
    *,
    theme: Optional[str],
    render_locals: Callable[[Frame], Iterable[ConsoleRenderable]],
) -> Iterable[Union[str, Text, Columns, Syntax]]:
    if frame.filename.startswith("<"):
        yield from render_locals(frame)
        return
    suppressed = any(
        frame.filename.startswith(path) for path in traceback.suppress
    )
    if suppressed:
        return
    try:
        code_lines = linecache.getlines(frame.filename)
        code = "".join(code_lines)
        if not code:
            return
        lexer_name = traceback._guess_lexer(frame.filename, code)
        syntax = Syntax(
            code,
            lexer_name,
            theme=theme,
            line_numbers=True,
            line_range=(
                frame.lineno - traceback.extra_lines,
                frame.lineno + traceback.extra_lines,
            ),
            highlight_lines={frame.lineno},
            word_wrap=traceback.word_wrap,
            code_width=traceback.code_width,
            indent_guides=traceback.indent_guides,
            dedent=False,
        )
        yield ""
    except Exception as error:
        yield Text.assemble((f"\n{error}", "traceback.error"))
        return
    _traceback_stylize_last_instruction(syntax, frame, code_lines)
    yield (
        Columns([syntax, *render_locals(frame)], padding=1)
        if frame.locals
        else syntax
    )


class PathHighlighter(RegexHighlighter):
    highlights = [r"(?P<dim>.*/)(?P<bold>.+)"]


class Traceback:
    """A Console renderable that renders a traceback.

    Args:
        trace (Trace, optional): A `Trace` object produced from `extract`. Defaults to None, which uses
            the last exception.
        width (Optional[int], optional): Number of characters used to traceback. Defaults to 100.
        code_width (Optional[int], optional): Number of code characters used to traceback. Defaults to 88.
        extra_lines (int, optional): Additional lines of code to render. Defaults to 3.
        theme (str, optional): Override pygments theme used in traceback.
        word_wrap (bool, optional): Enable word wrapping of long lines. Defaults to False.
        show_locals (bool, optional): Enable display of local variables. Defaults to False.
        indent_guides (bool, optional): Enable indent guides in code and locals. Defaults to True.
        locals_max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
            Defaults to 10.
        locals_max_string (int, optional): Maximum length of string before truncating, or None to disable. Defaults to 80.
        locals_max_depth (int, optional): Maximum depths of locals before truncating, or None to disable. Defaults to None.
        locals_hide_dunder (bool, optional): Hide locals prefixed with double underscore. Defaults to True.
        locals_hide_sunder (bool, optional): Hide locals prefixed with single underscore. Defaults to False.
        locals_overflow (OverflowMethod, optional): How to handle overflowing locals, or None to disable. Defaults to None.
        suppress (Sequence[Union[str, ModuleType]]): Optional sequence of modules or paths to exclude from traceback.
        max_frames (int): Maximum number of frames to show in a traceback, 0 for no maximum. Defaults to 100.

    """

    LEXERS = {
        "": "text",
        ".py": "python",
        ".pxd": "cython",
        ".pyx": "cython",
        ".pxi": "pyrex",
    }

    def _init_suppress_paths(self, suppress: Iterable[Union[str, ModuleType]]) -> None:
        self.suppress = []
        for suppress_entity in suppress:
            if isinstance(suppress_entity, str):
                path = suppress_entity
            else:
                assert (
                    suppress_entity.__file__ is not None
                ), f"{suppress_entity!r} must be a module with '__file__' attribute"
                path = os.path.dirname(suppress_entity.__file__)
            self.suppress.append(os.path.normpath(os.path.abspath(path)))

    def __init__(
        self,
        trace: Optional[Trace] = None,
        *,
        width: Optional[int] = 100,
        code_width: Optional[int] = 88,
        extra_lines: int = 3,
        theme: Optional[str] = None,
        word_wrap: bool = False,
        show_locals: bool = False,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_max_depth: Optional[int] = None,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = False,
        locals_overlow: Optional[OverflowMethod] = None,
        indent_guides: bool = True,
        suppress: Iterable[Union[str, ModuleType]] = (),
        max_frames: int = 100,
    ):
        if trace is None:
            exc_type, exc_value, traceback = sys.exc_info()
            if exc_type is None or exc_value is None or traceback is None:
                raise ValueError(
                    "Value for 'trace' required if not called in except: block"
                )
            trace = self.extract(
                exc_type, exc_value, traceback, show_locals=show_locals
            )
        self.trace = trace
        self.width = width
        self.code_width = code_width
        self.extra_lines = extra_lines
        self.theme = Syntax.get_theme(theme or "ansi_dark")
        self.word_wrap = word_wrap
        self.show_locals = show_locals
        self.indent_guides = indent_guides
        self.locals_max_length = locals_max_length
        self.locals_max_string = locals_max_string
        self.locals_max_depth = locals_max_depth
        self.locals_hide_dunder = locals_hide_dunder
        self.locals_hide_sunder = locals_hide_sunder
        self.locals_overflow = locals_overlow

        self._init_suppress_paths(suppress)
        self.max_frames = max(4, max_frames) if max_frames > 0 else 0

    @classmethod
    def from_exception(
        cls,
        exc_type: Type[Any],
        exc_value: BaseException,
        traceback: Optional[TracebackType],
        *,
        width: Optional[int] = 100,
        code_width: Optional[int] = 88,
        extra_lines: int = 3,
        theme: Optional[str] = None,
        word_wrap: bool = False,
        show_locals: bool = False,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_max_depth: Optional[int] = None,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = False,
        locals_overflow: Optional[OverflowMethod] = None,
        indent_guides: bool = True,
        suppress: Iterable[Union[str, ModuleType]] = (),
        max_frames: int = 100,
    ) -> "Traceback":
        """Create a traceback from exception info

        Args:
            exc_type (Type[BaseException]): Exception type.
            exc_value (BaseException): Exception value.
            traceback (TracebackType): Python Traceback object.
            width (Optional[int], optional): Number of characters used to traceback. Defaults to 100.
            code_width (Optional[int], optional): Number of code characters used to traceback. Defaults to 88.
            extra_lines (int, optional): Additional lines of code to render. Defaults to 3.
            theme (str, optional): Override pygments theme used in traceback.
            word_wrap (bool, optional): Enable word wrapping of long lines. Defaults to False.
            show_locals (bool, optional): Enable display of local variables. Defaults to False.
            indent_guides (bool, optional): Enable indent guides in code and locals. Defaults to True.
            locals_max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
                Defaults to 10.
            locals_max_depth (int, optional): Maximum depths of locals before truncating, or None to disable. Defaults to None.
            locals_max_string (int, optional): Maximum length of string before truncating, or None to disable. Defaults to 80.
            locals_hide_dunder (bool, optional): Hide locals prefixed with double underscore. Defaults to True.
            locals_hide_sunder (bool, optional): Hide locals prefixed with single underscore. Defaults to False.
            locals_overflow (OverflowMethod, optional): How to handle overflowing locals, or None to disable. Defaults to None.
            suppress (Iterable[Union[str, ModuleType]]): Optional sequence of modules or paths to exclude from traceback.
            max_frames (int): Maximum number of frames to show in a traceback, 0 for no maximum. Defaults to 100.

        Returns:
            Traceback: A Traceback instance that may be printed.
        """
        rich_traceback = cls.extract(
            exc_type,
            exc_value,
            traceback,
            show_locals=show_locals,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            locals_max_depth=locals_max_depth,
            locals_hide_dunder=locals_hide_dunder,
            locals_hide_sunder=locals_hide_sunder,
        )

        return cls(
            rich_traceback,
            width=width,
            code_width=code_width,
            extra_lines=extra_lines,
            theme=theme,
            word_wrap=word_wrap,
            show_locals=show_locals,
            indent_guides=indent_guides,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            locals_max_depth=locals_max_depth,
            locals_hide_dunder=locals_hide_dunder,
            locals_hide_sunder=locals_hide_sunder,
            locals_overlow=locals_overflow,
            suppress=suppress,
            max_frames=max_frames,
        )

    @classmethod
    def extract(
        cls,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: Optional[TracebackType],
        *,
        show_locals: bool = False,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_max_depth: Optional[int] = None,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = False,
        _visited_exceptions: Optional[Set[BaseException]] = None,
    ) -> Trace:
        """Extract traceback information.

        Args:
            exc_type (Type[BaseException]): Exception type.
            exc_value (BaseException): Exception value.
            traceback (TracebackType): Python Traceback object.
            show_locals (bool, optional): Enable display of local variables. Defaults to False.
            locals_max_length (int, optional): Maximum length of containers before abbreviating, or None for no abbreviation.
                Defaults to 10.
            locals_max_string (int, optional): Maximum length of string before truncating, or None to disable. Defaults to 80.
            locals_max_depth (int, optional): Maximum depths of locals before truncating, or None to disable. Defaults to None.
            locals_hide_dunder (bool, optional): Hide locals prefixed with double underscore. Defaults to True.
            locals_hide_sunder (bool, optional): Hide locals prefixed with single underscore. Defaults to False.

        Returns:
            Trace: A Trace instance which you can use to construct a `Traceback`.
        """

        stacks: List[Stack] = []
        is_cause = False

        _IMPORT_CWD = import_attr('rich', '_IMPORT_CWD')

        notes: List[str] = getattr(exc_value, "__notes__", None) or []

        grouped_exceptions: Set[BaseException] = (
            set() if _visited_exceptions is None else _visited_exceptions
        )

        while True:
            stack = Stack(
                exc_type=_traceback_safe_str(exc_type.__name__),
                exc_value=_traceback_safe_str(exc_value),
                is_cause=is_cause,
                notes=notes,
            )

            _traceback_append_exception_group(
                stack,
                exc_value,
                grouped_exceptions,
                cls.extract,
                show_locals=show_locals,
                locals_max_length=locals_max_length,
                locals_max_string=locals_max_string,
                locals_hide_dunder=locals_hide_dunder,
                locals_hide_sunder=locals_hide_sunder,
            )
            _traceback_set_syntax_error(stack, exc_value, notes)
            stacks.append(stack)
            _traceback_walk_stack_frames(
                stack,
                traceback,
                import_cwd=_IMPORT_CWD,
                show_locals=show_locals,
                locals_max_length=locals_max_length,
                locals_max_string=locals_max_string,
                locals_max_depth=locals_max_depth,
                locals_hide_dunder=locals_hide_dunder,
                locals_hide_sunder=locals_hide_sunder,
            )

            linked = _traceback_next_linked_exception(exc_value, grouped_exceptions)
            if linked is None:
                break  # pragma: no cover
            exc_type, exc_value, traceback, is_cause = linked

        return Trace(stacks=stacks)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        theme = self.theme
        background_style = theme.get_background_style()
        token_style = theme.get_style_for_token

        traceback_theme = Theme(
            {
                "pretty": token_style(TextToken),
                "pygments.text": token_style(Token),
                "pygments.string": token_style(String),
                "pygments.function": token_style(Name.Function),
                "pygments.number": token_style(Number),
                "repr.indent": token_style(Comment) + Style(dim=True),
                "repr.str": token_style(String),
                "repr.brace": token_style(TextToken) + Style(bold=True),
                "repr.number": token_style(Number),
                "repr.bool_true": token_style(Keyword.Constant),
                "repr.bool_false": token_style(Keyword.Constant),
                "repr.none": token_style(Keyword.Constant),
                "scope.border": token_style(String.Delimiter),
                "scope.equals": token_style(Operator),
                "scope.key": token_style(Name),
                "scope.key.special": token_style(Name.Constant) + Style(dim=True),
            },
            inherit=False,
        )

        highlighter = ReprHighlighter()

        @group()
        def render_stack(stack: Stack, last: bool) -> RenderResult:
            if stack.frames:
                stack_renderable: ConsoleRenderable = Panel(
                    self._render_stack(stack),
                    title="[traceback.title]Traceback [dim](most recent call last)",
                    style=background_style,
                    border_style="traceback.border",
                    expand=True,
                    padding=(0, 1),
                )
                stack_renderable = Constrain(stack_renderable, self.width)
                with console.use_theme(traceback_theme):
                    yield stack_renderable

            if stack.syntax_error is not None:
                with console.use_theme(traceback_theme):
                    yield Constrain(
                        Panel(
                            self._render_syntax_error(stack.syntax_error),
                            style=background_style,
                            border_style="traceback.border.syntax_error",
                            expand=True,
                            padding=(0, 1),
                            width=self.width,
                        ),
                        self.width,
                    )
                yield Text.assemble(
                    (f"{stack.exc_type}: ", "traceback.exc_type"),
                    highlighter(stack.syntax_error.msg),
                )
            elif stack.exc_value:
                yield Text.assemble(
                    (f"{stack.exc_type}: ", "traceback.exc_type"),
                    highlighter(stack.exc_value),
                )
            else:
                yield Text.assemble((f"{stack.exc_type}", "traceback.exc_type"))

            for note in stack.notes:
                yield Text.assemble(("[NOTE] ", "traceback.note"), highlighter(note))

            if stack.is_group:
                for group_no, group_exception in enumerate(stack.exceptions, 1):
                    grouped_exceptions: List[Group] = []
                    for group_last, group_stack in loop_last(group_exception.stacks):
                        grouped_exceptions.append(render_stack(group_stack, group_last))
                    yield ""
                    yield Constrain(
                        Panel(
                            Group(*grouped_exceptions),
                            title=f"Sub-exception #{group_no}",
                            border_style="traceback.group.border",
                        ),
                        self.width,
                    )

            if not last:
                if stack.is_cause:
                    yield Text.from_markup(
                        "\n[i]The above exception was the direct cause of the following exception:\n",
                    )
                else:
                    yield Text.from_markup(
                        "\n[i]During handling of the above exception, another exception occurred:\n",
                    )

        for last, stack in loop_last(reversed(self.trace.stacks)):
            yield render_stack(stack, last)

    @group()
    def _render_syntax_error(self, syntax_error: _SyntaxError) -> RenderResult:
        highlighter = ReprHighlighter()
        path_highlighter = PathHighlighter()
        if syntax_error.filename != "<stdin>":
            if os.path.exists(syntax_error.filename):
                text = Text.assemble(
                    (f" {syntax_error.filename}", "pygments.string"),
                    (":", "pygments.text"),
                    (str(syntax_error.lineno), "pygments.number"),
                    style="pygments.text",
                )
                yield path_highlighter(text)
        syntax_error_text = highlighter(syntax_error.line.rstrip())
        syntax_error_text.no_wrap = True
        offset = min(syntax_error.offset - 1, len(syntax_error_text))
        syntax_error_text.stylize("bold underline", offset, offset)
        syntax_error_text += Text.from_markup(
            "\n" + " " * offset + "[traceback.offset]▲[/]",
            style="pygments.text",
        )
        yield syntax_error_text

    @classmethod
    def _guess_lexer(cls, filename: str, code: str) -> str:
        ext = os.path.splitext(filename)[-1]
        if not ext:
            # No extension, look at first line to see if it is a hashbang
            # Note, this is an educated guess and not a guarantee
            # If it fails, the only downside is that the code is highlighted strangely
            new_line_index = code.index("\n")
            first_line = code[:new_line_index] if new_line_index != -1 else code
            if first_line.startswith("#!") and "python" in first_line.lower():
                return "python"
        try:
            return cls.LEXERS.get(ext) or guess_lexer_for_filename(filename, code).name
        except ClassNotFound:
            return "text"

    @group()
    def _render_stack(self, stack: Stack) -> RenderResult:
        path_highlighter = PathHighlighter()
        theme = self.theme

        def render_locals(frame: Frame) -> Iterable[ConsoleRenderable]:
            yield from _traceback_render_locals(
                frame,
                indent_guides=self.indent_guides,
                locals_max_length=self.locals_max_length,
                locals_max_string=self.locals_max_string,
                locals_max_depth=self.locals_max_depth,
                locals_overflow=self.locals_overflow,
            )

        exclude_frames: Optional[range] = None
        if self.max_frames != 0:
            exclude_frames = range(
                self.max_frames // 2,
                len(stack.frames) - self.max_frames // 2,
            )

        excluded = False
        for frame_index, frame in enumerate(stack.frames):
            if exclude_frames and frame_index in exclude_frames:
                excluded = True
                continue

            if excluded:
                assert exclude_frames is not None
                yield Text(
                    f"\n... {len(exclude_frames)} frames hidden ...",
                    justify="center",
                    style="traceback.error",
                )
                excluded = False

            first = frame_index == 0
            if not frame.filename.startswith("<") and not first:
                yield ""
            yield _traceback_frame_header_text(
                frame, path_highlighter=path_highlighter, first=first
            )
            yield from _traceback_render_frame_code(
                frame,
                self,
                theme=theme,
                render_locals=render_locals,
            )


if __name__ == "__main__":  # pragma: no cover
    install(show_locals=True)
    import sys

    def bar(
        a: Any,
    ) -> None:  # 这是对亚洲语言支持的测试。面对模棱两可的想法，拒绝猜测的诱惑
        one = 1
        print(one / a)

    def foo(a: Any) -> None:
        _rich_traceback_guard = True
        bar(a)

    def error() -> None:
        foo(0)

    error()
