from __future__ import annotations

import os
import sys

from ._pick import (
    M_CONSOLE,
    M_JUPYTER_HTML,
    M_PRETTY,
    M_SEGMENT,
    rich_module,
)
from typing import Any, Callable, Dict, IO, Iterable, Iterator, List, Optional, Sequence, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ._types import Console, ConsoleRenderable, HighlighterType, JustifyMethod, Pager, Text


StyledPart = Tuple[str, Optional[str], Optional[str]]

def segments_to_styled_parts(segments: Iterable[Any]) -> Iterator[StyledPart]:
    """Convert Rich segments to HTML styling tuples."""
    Segment = rich_module(M_SEGMENT).Segment
    from .terminal_theme import DEFAULT_TERMINAL_THEME

    theme = DEFAULT_TERMINAL_THEME
    for text, style, control in Segment.simplify(segments):
        if control:
            continue
        rule = style.get_html_style(theme) if style else None
        link = style.link if style else None
        yield (text, rule, link)

def render_mimebundle(
    renderable: Any,
    include: Sequence[str],
    exclude: Sequence[str],
    **kwargs: Any,
) -> Dict[str, str]:
    _jupyter_html = rich_module(M_JUPYTER_HTML)
    console = rich_module(M_CONSOLE).get_console()

    segments = list(console.render(renderable, console.options))
    html = _jupyter_html.render_styled_parts(segments_to_styled_parts(segments))
    text = console._render_buffer(segments)
    return _jupyter_html._filter_mimebundle(
        {"text/plain": text, "text/html": html}, include, exclude
    )

def get_fileno(file_like: IO[str]) -> int | None:
    """Get fileno() from a file, accounting for poorly implemented file-like objects."""
    fileno: Callable[[], int] | None = getattr(file_like, "fileno", None)
    if fileno is not None:
        try:
            return fileno()
        except Exception:
            return None
    return None

WINDOWS = sys.platform == "win32"

_STDOUT_FILENO = 1
_STDERR_FILENO = 2
_STD_STREAMS_OUTPUT = (_STDOUT_FILENO, _STDERR_FILENO)

_MAX_WRITE = 32 * 1024 // 4

def is_jupyter() -> bool:  # pragma: no cover
    """Check if we're running in a Jupyter notebook."""
    try:
        get_ipython = __import__("IPython", fromlist=["get_ipython"]).get_ipython
    except (ImportError, AttributeError):
        return False
    ipython = get_ipython()
    shell = ipython.__class__.__name__
    if (
        "google.colab" in str(ipython.__class__)
        or os.getenv("DATABRICKS_RUNTIME_VERSION")
        or shell == "ZMQInteractiveShell"
    ):
        return True
    elif shell == "TerminalInteractiveShell":
        return False
    else:
        return False

def write_text_batched(write: Callable[[str], int], text: str) -> None:
    if len(text) <= _MAX_WRITE:
        write(text)
        return
    batch: List[str] = []
    batch_append = batch.append
    size = 0
    for line in text.splitlines(True):
        if size + len(line) > _MAX_WRITE and batch:
            write("".join(batch))
            batch.clear()
            size = 0
        batch_append(line)
        size += len(line)
    if batch:
        write("".join(batch))

def write_unicode_error(error: UnicodeEncodeError) -> None:
    error.reason = (
        f"{error.reason}\n*** You may need to add PYTHONIOENCODING=utf-8 to your environment ***"
    )
    raise error

def collect_renderables_is_expandable(obj: object) -> bool:
    return rich_module(M_PRETTY).is_expandable(obj)

def collect_renderables_add_object(
    console: "Console",
    renderable: object,
    *,
    text: List["Text"],
    append_text: Callable[["Text"], None],
    append: Callable[["ConsoleRenderable"], None],
    sep: str,
    end: str,
    justify: Optional["JustifyMethod"],
    emoji: Optional[bool],
    markup: Optional[bool],
    highlight: Optional[bool],
    highlighter: "HighlighterType",
) -> None:
    from .protocol import rich_cast

    from .text import Text

    renderable = rich_cast(renderable)
    if isinstance(renderable, str):
        append_text(
            console.render_str(
                renderable,
                emoji=emoji,
                markup=markup,
                highlight=highlight,
                highlighter=highlighter,
            )
        )
        return
    if isinstance(renderable, Text):
        append_text(renderable)
        return
    if hasattr(renderable, "__rich_console__"):
        collect_renderables_flush_text(text, sep, end, justify, append)
        append(renderable)
        return
    if collect_renderables_is_expandable(renderable):
        collect_renderables_flush_text(text, sep, end, justify, append)
        Pretty = rich_module(M_PRETTY).Pretty
        append(Pretty(renderable, highlighter=highlighter))
        return
    append_text(highlighter(str(renderable)))

def collect_renderables_flush_text(
    text: List["Text"],
    sep: str,
    end: str,
    justify: Optional["JustifyMethod"],
    append: Callable[["ConsoleRenderable"], None],
) -> None:
    if not text:
        return
    from .text import Text

    sep_text = Text(sep, justify=justify, end=end)
    append(sep_text.join(text))
    text.clear()

def write_buffer_jupyter(console: "Console") -> None:
    from ._jupyter_html import display_html, render_styled_parts

    segments = console._buffer[:]
    html = render_styled_parts(segments_to_styled_parts(segments))
    text = console._render_buffer(segments)
    display_html(html, text)
    del console._buffer[:]

def write_buffer_legacy_windows(console: "Console") -> None:
    from rich._win32_console import LegacyWindowsTerm
    from importlib import import_module

    legacy_windows_render = import_module("rich._windows_renderer").legacy_windows_render

    Segment = rich_module(M_SEGMENT).Segment
    buffer = console._buffer[:]
    if console.no_color and console._color_system:
        buffer = list(Segment.remove_color(buffer))
    legacy_windows_render(buffer, LegacyWindowsTerm(console.file))

def pager_context_exit(
    console: "Console",
    pager: "Pager",
    exc_type: Optional[type],
    *,
    styles: bool,
    links: bool,
) -> None:
    """Flush pager buffer on successful context exit."""
    if exc_type is not None:
        return
    Segment = rich_module(M_SEGMENT).Segment
    with console._lock:
        buffer = console._buffer[:]
        del console._buffer[:]
        segments = buffer
        if not styles:
            segments = Segment.strip_styles(segments)
        elif not links:
            segments = Segment.strip_links(segments)
        content = console._render_buffer(segments)
    pager.show(content)

def console_log_renderables(
    console: "Console",
    renderables: list,
) -> None:
    """Render log output and append lines to the console buffer."""
    Segment = rich_module(M_SEGMENT).Segment
    new_segments: List["Segment"] = []
    extend = new_segments.extend
    render = console.render
    render_options = console.options
    for renderable in renderables:
        extend(render(renderable, render_options))
    buffer_extend = console._buffer.extend
    for line in Segment.split_and_crop_lines(
        new_segments, console.width, pad=False
    ):
        buffer_extend(line)

def write_buffer_terminal(console: "Console") -> None:
    if WINDOWS and console.legacy_windows:
        fileno = get_fileno(console.file)
        if fileno is not None and fileno in _STD_STREAMS_OUTPUT:
            write_buffer_legacy_windows(console)
            console.file.flush()
            del console._buffer[:]
            return

    text = console._render_buffer(console._buffer[:])
    try:
        if WINDOWS:
            write_text_batched(console.file.write, text)
        else:
            console.file.write(text)
    except UnicodeEncodeError as error:
        write_unicode_error(error)
    console.file.flush()
    del console._buffer[:]