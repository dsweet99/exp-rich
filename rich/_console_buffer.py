"""Console buffer flush helpers."""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Iterable, List, Optional, TextIO

from ._fileno import get_fileno

WINDOWS = sys.platform == "win32"
try:
    _STDOUT_FILENO = sys.__stdout__.fileno()
except Exception:
    _STDOUT_FILENO = 1
try:
    _STDERR_FILENO = sys.__stderr__.fileno()
except Exception:
    _STDERR_FILENO = 2
_STD_STREAMS_OUTPUT = (_STDOUT_FILENO, _STDERR_FILENO)
_MAX_WRITE = 32 * 1024 // 4


def _segment():
    return sys.modules["rich.segment"].Segment


def _append_record_buffer(console: "Console") -> None:
    if not console.record or console._buffer_index:
        return
    with console._record_buffer_lock:
        console._record_buffer.extend(console._buffer[:])


def _flush_jupyter_buffer(console: "Console") -> None:
    display = sys.modules["rich.jupyter"].display
    display(console._buffer, console._render_buffer(console._buffer[:]))
    del console._buffer[:]


def _use_legacy_windows_render(console: "Console") -> bool:
    if not console.legacy_windows:
        return False
    fileno = get_fileno(console.file)
    return fileno is not None and fileno in _STD_STREAMS_OUTPUT


def _flush_legacy_windows_buffer(console: "Console") -> None:
    Segment = _segment()
    LegacyWindowsTerm = sys.modules["rich._win32_console"].LegacyWindowsTerm
    legacy_windows_render = sys.modules["rich._windows_renderer"].legacy_windows_render
    buffer = console._buffer[:]
    if console.no_color and console._color_system:
        buffer = list(Segment.remove_color(buffer))
    legacy_windows_render(buffer, LegacyWindowsTerm(console.file))


def _write_text_batched(file: TextIO, text: str) -> None:
    write = file.write
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


def _write_text_with_encoding_hint(file: TextIO, text: str) -> None:
    try:
        _write_text_batched(file, text)
    except UnicodeEncodeError as error:
        error.reason = (
            f"{error.reason}\n*** You may need to add PYTHONIOENCODING=utf-8 to your environment ***"
        )
        raise


def _flush_modern_windows_buffer(console: "Console") -> None:
    text = console._render_buffer(console._buffer[:])
    _write_text_with_encoding_hint(console.file, text)


def _flush_posix_buffer(console: "Console") -> None:
    text = console._render_buffer(console._buffer[:])
    try:
        console.file.write(text)
    except UnicodeEncodeError as error:
        error.reason = (
            f"{error.reason}\n*** You may need to add PYTHONIOENCODING=utf-8 to your environment ***"
        )
        raise


def _flush_non_jupyter_buffer(console: "Console") -> None:
    if WINDOWS:
        if _use_legacy_windows_render(console):
            _flush_legacy_windows_buffer(console)
        else:
            _flush_modern_windows_buffer(console)
    else:
        _flush_posix_buffer(console)
    console.file.flush()
    del console._buffer[:]


def write_console_buffer(console: "Console") -> None:
    """Flush the console buffer to the output file."""
    with console._lock:
        _append_record_buffer(console)
        if console._buffer_index != 0:
            return
        if console.is_jupyter:
            _flush_jupyter_buffer(console)
        else:
            _flush_non_jupyter_buffer(console)


def flush_pager_buffer(
    console: "Console", *, styles: bool, links: bool, pager
) -> None:
    """Flush pager buffer contents through the pager."""
    Segment = _segment()
    with console._lock:
        buffer: List = console._buffer[:]
        del console._buffer[:]
        segments: Iterable = buffer
        if not styles:
            segments = Segment.strip_styles(segments)
        elif not links:
            segments = Segment.strip_links(segments)
        content = console._render_buffer(segments)
    pager(content)


def read_console_input(*, password: bool, stream: Optional[TextIO]) -> str:
    """Read input from stdin, a stream, or getpass."""
    if password:
        import getpass as _getpass_mod

        return _getpass_mod.getpass("", stream=stream)
    if stream:
        return stream.readline()
    return input()
