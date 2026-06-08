"""Console buffer output helpers with no rich module imports."""
from __future__ import annotations

import sys
from typing import Callable, List, TypeVar

T = TypeVar("T")

WINDOWS = sys.platform == "win32"

try:
    _STDOUT_FILENO = sys.__stdout__.fileno()  # type: ignore[union-attr]
except Exception:
    _STDOUT_FILENO = 1
try:
    _STDERR_FILENO = sys.__stderr__.fileno()  # type: ignore[union-attr]
except Exception:
    _STDERR_FILENO = 2

_STD_STREAMS_OUTPUT = (_STDOUT_FILENO, _STDERR_FILENO)
_BUFFER_MAX_WRITE = 32 * 1024 // 4


def copy_to_record_buffer(console: T, buffer: list) -> None:
    if console.record and not console._buffer_index:
        with console._record_buffer_lock:
            console._record_buffer.extend(buffer[:])


def use_legacy_windows_render(
    console: T, get_fileno: Callable[[object], object | None]
) -> bool:
    if not console.legacy_windows:
        return False
    fileno = get_fileno(console.file)
    if fileno is None:
        return False
    return fileno in _STD_STREAMS_OUTPUT


def write_text_in_batches(write: Callable[[str], object], text: str) -> None:
    if len(text) <= _BUFFER_MAX_WRITE:
        write(text)
        return
    batch: List[str] = []
    batch_append = batch.append
    size = 0
    for line in text.splitlines(True):
        if size + len(line) > _BUFFER_MAX_WRITE and batch:
            write("".join(batch))
            batch.clear()
            size = 0
        batch_append(line)
        size += len(line)
    if batch:
        write("".join(batch))
        batch.clear()


def write_text_to_file(file, text: str) -> None:
    try:
        write_text_in_batches(file.write, text)
    except UnicodeEncodeError as error:
        error.reason = (
            f"{error.reason}\n*** You may need to add PYTHONIOENCODING=utf-8 "
            "to your environment ***"
        )
        raise


def flush_and_clear(file, buffer: list) -> None:
    file.flush()
    del buffer[:]


def flush_jupyter_buffer(buffer: list, render_buffer_fn) -> None:
    import importlib

    display = importlib.import_module(".jupyter", __package__).display
    display(buffer, render_buffer_fn(buffer[:]))
    del buffer[:]


def flush_legacy_windows_to_file(
    console: T, buffer: list, render_buffer_fn, segment_class
) -> None:
    import importlib

    LegacyWindowsTerm = importlib.import_module("._win32_console", __package__).LegacyWindowsTerm
    legacy_windows_render = importlib.import_module("._windows_renderer", __package__).legacy_windows_render

    buf = buffer[:]
    if console.no_color and console._color_system:
        buf = list(segment_class().remove_color(buf))
    legacy_windows_render(buf, LegacyWindowsTerm(console.file))
    flush_and_clear(console.file, buffer)


def flush_modern_windows_to_file(console: T, buffer: list, render_buffer_fn) -> None:
    text = render_buffer_fn(buffer[:])
    write_text_to_file(console.file, text)
    flush_and_clear(console.file, buffer)


def flush_posix_to_file(console: T, buffer: list, render_buffer_fn) -> None:
    text = render_buffer_fn(buffer[:])
    try:
        console.file.write(text)
    except UnicodeEncodeError as error:
        error.reason = (
            f"{error.reason}\n*** You may need to add PYTHONIOENCODING=utf-8 "
            "to your environment ***"
        )
        raise
    flush_and_clear(console.file, buffer)


def flush_console_buffer(
    console: T,
    buffer: list,
    render_buffer_fn,
    get_fileno_fn,
    segment_cls,
    *,
    windows: bool,
    is_jupyter: bool,
) -> None:
    """Dispatch buffer flush by platform."""
    if is_jupyter:
        flush_jupyter_buffer(buffer, render_buffer_fn)
        return
    if windows:
        if use_legacy_windows_render(console, get_fileno_fn):
            flush_legacy_windows_to_file(
                console, buffer, render_buffer_fn, segment_cls
            )
        else:
            flush_modern_windows_to_file(console, buffer, render_buffer_fn)
        return
    flush_posix_to_file(console, buffer, render_buffer_fn)
