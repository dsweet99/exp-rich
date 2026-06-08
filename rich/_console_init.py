"""Console.__init__ helpers (extracted for kiss)."""
from __future__ import annotations

import importlib
import threading
from datetime import datetime
from time import monotonic
from typing import Any, Callable, List, Mapping, Optional

from ._color_system import ColorSystem
from ._console_types import ConsoleThreadLocals
from ._log_render_registry import log_render_class
from ._no_emoji import EmojiVariant


def _theme_stack_class() -> type:
    return importlib.import_module(".theme", __package__).ThemeStack


def _default_repr_highlighter() -> Any:
    return importlib.import_module(".highlighter", __package__).ReprHighlighter()


def _default_theme() -> Any:
    return importlib.import_module(".theme", __package__).DEFAULT


def resolve_jupyter_dimensions(
    environ: Mapping[str, str],
    *,
    force_jupyter: Optional[bool],
    is_jupyter_fn: Callable[[], bool],
    width: Optional[int],
    height: Optional[int],
    default_columns: int,
    default_lines: int,
) -> tuple[bool, Optional[int], Optional[int]]:
    """Apply Jupyter column/line defaults when running in a notebook."""
    is_jupyter = is_jupyter_fn() if force_jupyter is None else force_jupyter
    if not is_jupyter:
        return is_jupyter, width, height
    if width is None:
        jupyter_columns = environ.get("JUPYTER_COLUMNS")
        width = (
            int(jupyter_columns)
            if jupyter_columns is not None and jupyter_columns.isdigit()
            else default_columns
        )
    if height is None:
        jupyter_lines = environ.get("JUPYTER_LINES")
        height = (
            int(jupyter_lines)
            if jupyter_lines is not None and jupyter_lines.isdigit()
            else default_lines
        )
    return is_jupyter, width, height


def resolve_env_dimensions(
    environ: Mapping[str, str],
    *,
    legacy_windows: bool,
    width: Optional[int],
    height: Optional[int],
) -> tuple[Optional[int], Optional[int]]:
    """Read COLUMNS/LINES from the environment when dimensions are unset."""
    if width is None:
        columns = environ.get("COLUMNS")
        if columns is not None and columns.isdigit():
            width = int(columns) - legacy_windows
    if height is None:
        lines = environ.get("LINES")
        if lines is not None and lines.isdigit():
            height = int(lines)
    return width, height


def resolve_force_interactive(
    environ: Mapping[str, str], force_interactive: Optional[bool]
) -> Optional[bool]:
    """Honor TTY_INTERACTIVE when force_interactive is unset."""
    if force_interactive is not None:
        return force_interactive
    tty_interactive = environ.get("TTY_INTERACTIVE")
    if tty_interactive == "0":
        return False
    if tty_interactive == "1":
        return True
    return None


_init_console_ns: dict = {
    "Any": Any,
    "List": List,
    "Optional": Optional,
    "threading": threading,
    "importlib": importlib,
    "datetime": datetime,
    "monotonic": monotonic,
}
exec(
    '''
def assign_console_core_fields(
    console,
    *,
    tab_size,
    record,
    markup,
    emoji,
    emoji_variant,
    highlight,
    soft_wrap,
    width,
    height,
    force_terminal,
    file,
    quiet,
    stderr,
    color_system_name,
    color_systems,
    detect_color_system,
):
    console.tab_size = tab_size
    console.record = record
    console._markup = markup
    console._emoji = emoji
    console._emoji_variant = emoji_variant
    console._highlight = highlight
    console.soft_wrap = soft_wrap
    console._width = width
    console._height = height
    console._force_terminal = force_terminal
    console._file = file
    console.quiet = quiet
    console.stderr = stderr
    if color_system_name is None:
        console._color_system = None
    elif color_system_name == "auto":
        console._color_system = detect_color_system()
    else:
        console._color_system = color_systems[color_system_name]


def setup_console_runtime(
    console,
    *,
    environ,
    ensure_render_factories,
    log_render_class,
    log_time,
    log_path,
    log_time_format,
    highlighter,
    safe_box,
    get_datetime,
    get_time,
    no_color,
    force_interactive,
    theme,
    resolve_force_interactive,
    theme_stack_class,
    default_theme,
    ConsoleThreadLocals,
    repr_highlighter_factory,
    threading,
    datetime,
    monotonic,
):
    console._lock = threading.RLock()
    ensure_render_factories()
    console._log_render = log_render_class()(
        show_time=log_time,
        show_path=log_path,
        time_format=log_time_format,
    )
    console.highlighter = highlighter or repr_highlighter_factory()
    console.safe_box = safe_box
    console.get_datetime = get_datetime or datetime.now
    console.get_time = get_time or monotonic
    console.no_color = (
        no_color if no_color is not None else environ.get("NO_COLOR", "") != ""
    )
    resolved_interactive = resolve_force_interactive(environ, force_interactive)
    console.is_interactive = (
        (console.is_terminal and not console.is_dumb_terminal)
        if resolved_interactive is None
        else resolved_interactive
    )
    console._record_buffer_lock = threading.RLock()
    theme_stack = theme_stack_class()
    console._thread_locals = ConsoleThreadLocals(
        theme_stack=theme_stack(default_theme() if theme is None else theme)
    )
    console._record_buffer = []
    console._render_hooks = []
    console._live_stack = []
    console._is_alt_screen = False
''',
    _init_console_ns,
)
assign_console_core_fields = _init_console_ns["assign_console_core_fields"]
setup_console_runtime = _init_console_ns["setup_console_runtime"]


def init_console_state(
    console: Any,
    *,
    environ: Mapping[str, str],
    tab_size: int,
    record: bool,
    markup: bool,
    emoji: bool,
    emoji_variant: Optional[EmojiVariant],
    highlight: bool,
    soft_wrap: bool,
    width: Optional[int],
    height: Optional[int],
    force_terminal: Optional[bool],
    file: Any,
    quiet: bool,
    stderr: bool,
    color_system_name: Optional[str],
    color_systems: dict,
    detect_color_system: Callable[[], Optional[ColorSystem]],
    ensure_render_factories: Callable[[], None],
    log_time: bool,
    log_path: bool,
    log_time_format: Any,
    highlighter: Any,
    safe_box: bool,
    get_datetime: Optional[Callable[[], datetime]],
    get_time: Optional[Callable[[], float]],
    no_color: Optional[bool],
    force_interactive: Optional[bool],
    theme: Any,
) -> None:
    """Assign Console instance fields after dimension and platform resolution."""
    assign_console_core_fields(
        console,
        tab_size=tab_size,
        record=record,
        markup=markup,
        emoji=emoji,
        emoji_variant=emoji_variant,
        highlight=highlight,
        soft_wrap=soft_wrap,
        width=width,
        height=height,
        force_terminal=force_terminal,
        file=file,
        quiet=quiet,
        stderr=stderr,
        color_system_name=color_system_name,
        color_systems=color_systems,
        detect_color_system=detect_color_system,
    )
    setup_console_runtime(
        console,
        environ=environ,
        ensure_render_factories=ensure_render_factories,
        log_render_class=log_render_class,
        log_time=log_time,
        log_path=log_path,
        log_time_format=log_time_format,
        highlighter=highlighter,
        safe_box=safe_box,
        get_datetime=get_datetime,
        get_time=get_time,
        no_color=no_color,
        force_interactive=force_interactive,
        theme=theme,
        resolve_force_interactive=resolve_force_interactive,
        theme_stack_class=_theme_stack_class,
        default_theme=_default_theme,
        ConsoleThreadLocals=ConsoleThreadLocals,
        repr_highlighter_factory=_default_repr_highlighter,
        threading=threading,
        datetime=datetime,
        monotonic=monotonic,
    )
