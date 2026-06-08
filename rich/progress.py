from __future__ import annotations

import io
import typing
import warnings
from abc import ABC, abstractmethod
from collections import deque
from datetime import timedelta
from io import RawIOBase, UnsupportedOperation
from math import ceil
from mmap import mmap
from operator import length_hint
from os import PathLike, stat
from threading import Event, RLock, Thread
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Callable,
    ContextManager,
    Deque,
    Dict,
    Iterable,
    List,
    Literal,
    NewType,
    Optional,
    TextIO,
    Tuple,
    Type,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    # Can be replaced with `from typing import Self` in Python 3.11+
    from typing_extensions import Self  # pragma: no cover

    from .highlighter import Highlighter

from .filesize import decimal, pick_unit_and_suffix
from .console import get_console
from .console import Console, Group, JustifyMethod, RenderableType
from ._jupyter_mixin import JupyterMixin
from .live import Live
from .progress_bar import ProgressBar
from .spinner import Spinner
from .style import StyleType
from .table import Column, Table
from .text import Text, TextType

TaskID = NewType("TaskID", int)

ProgressType = TypeVar("ProgressType")

GetTimeCallable = Callable[[], float]


_I = typing.TypeVar("_I", TextIO, BinaryIO)



def _track_thread_init(
    self, progress: "Progress", task_id: "TaskID", update_period: float
) -> None:
    self.progress = progress
    self.task_id = task_id
    self.update_period = update_period
    self.done = Event()
    self.completed = 0
    Thread.__init__(self, daemon=True)


def _track_thread_run(self) -> None:
    task_id = self.task_id
    advance = self.progress.advance
    update_period = self.update_period
    last_completed = 0
    wait = self.done.wait
    while not wait(update_period) and self.progress.live.is_started:
        completed = self.completed
        if last_completed != completed:
            advance(task_id, completed - last_completed)
            last_completed = completed
    self.progress.update(self.task_id, completed=self.completed, refresh=True)


def _track_thread_enter(self) -> "_TrackThread":
    self.start()
    return self


def _track_thread_exit(
    self,
    exc_type: Optional[Type[BaseException]],
    exc_val: Optional[BaseException],
    exc_tb: Optional[TracebackType],
) -> None:
    self.done.set()
    self.join()


_TrackThread = type(
    "_TrackThread",
    (Thread,),
    {
        "__doc__": "A thread to periodically update progress.",
        "__init__": _track_thread_init,
        "run": _track_thread_run,
        "__enter__": _track_thread_enter,
        "__exit__": _track_thread_exit,
    },
)


def track(
    sequence: Iterable[ProgressType],
    description: str = "Working...",
    total: Optional[float] = None,
    completed: int = 0,
    auto_refresh: bool = True,
    console: Optional[Console] = None,
    transient: bool = False,
    get_time: Optional[Callable[[], float]] = None,
    refresh_per_second: float = 10,
    style: StyleType = "bar.back",
    complete_style: StyleType = "bar.complete",
    finished_style: StyleType = "bar.finished",
    pulse_style: StyleType = "bar.pulse",
    update_period: float = 0.1,
    disable: bool = False,
    show_speed: bool = True,
) -> Iterable[ProgressType]:
    """Track progress by iterating over a sequence.

    You can also track progress of an iterable, which might require that you additionally specify ``total``.

    Args:
        sequence (Iterable[ProgressType]): Values you wish to iterate over and track progress.
        description (str, optional): Description of task show next to progress bar. Defaults to "Working".
        total: (float, optional): Total number of steps. Default is len(sequence).
        completed (int, optional): Number of steps completed so far. Defaults to 0.
        auto_refresh (bool, optional): Automatic refresh, disable to force a refresh after each iteration. Default is True.
        transient: (bool, optional): Clear the progress on exit. Defaults to False.
        console (Console, optional): Console to write to. Default creates internal Console instance.
        refresh_per_second (float): Number of times per second to refresh the progress information. Defaults to 10.
        style (StyleType, optional): Style for the bar background. Defaults to "bar.back".
        complete_style (StyleType, optional): Style for the completed bar. Defaults to "bar.complete".
        finished_style (StyleType, optional): Style for a finished bar. Defaults to "bar.finished".
        pulse_style (StyleType, optional): Style for pulsing bars. Defaults to "bar.pulse".
        update_period (float, optional): Minimum time (in seconds) between calls to update(). Defaults to 0.1.
        disable (bool, optional): Disable display of progress.
        show_speed (bool, optional): Show speed if total isn't known. Defaults to True.
    Returns:
        Iterable[ProgressType]: An iterable of the values in the sequence.

    """

    columns: List["ProgressColumn"] = (
        [TextColumn("[progress.description]{task.description}")] if description else []
    )
    columns.extend(
        (
            BarColumn(
                style=style,
                complete_style=complete_style,
                finished_style=finished_style,
                pulse_style=pulse_style,
            ),
            TaskProgressColumn(show_speed=show_speed),
            TimeRemainingColumn(elapsed_when_finished=True),
        )
    )
    progress = Progress(
        *columns,
        auto_refresh=auto_refresh,
        console=console,
        transient=transient,
        get_time=get_time,
        refresh_per_second=refresh_per_second or 10,
        disable=disable,
    )

    with progress:
        yield from progress.track(
            sequence,
            total=total,
            completed=completed,
            description=description,
            update_period=update_period,
        )




def _reader__init__(
        self,
        handle: BinaryIO,
        progress: "Progress",
        task: TaskID,
        close_handle: bool = True,
    ) -> None:
        self.handle = handle
        self.progress = progress
        self.task = task
        self.close_handle = close_handle
        self._closed = False


def _reader__enter__(self) -> "_Reader":
        self.handle.__enter__()
        return self


def _reader__exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()


def _reader__iter__(self) -> BinaryIO:
        return self


def _reader__next__(self) -> bytes:
        line = next(self.handle)
        self.progress.advance(self.task, advance=len(line))
        return line


def _reader_closed(self) -> bool:
        return self._closed


def _reader_fileno(self) -> int:
        return self.handle.fileno()


def _reader_isatty(self) -> bool:
        return self.handle.isatty()


def _reader_mode(self) -> str:
        return self.handle.mode


def _reader_name(self) -> str:
        return self.handle.name


def _reader_readable(self) -> bool:
        return self.handle.readable()


def _reader_seekable(self) -> bool:
        return self.handle.seekable()


def _reader_writable(self) -> bool:
        return False


def _reader_read(self, size: int = -1) -> bytes:
        block = self.handle.read(size)
        self.progress.advance(self.task, advance=len(block))
        return block


def _reader_readinto(self, b: Union[bytearray, memoryview, mmap]):  # type: ignore[no-untyped-def, override]
        n = self.handle.readinto(b)  # type: ignore[attr-defined]
        self.progress.advance(self.task, advance=n)
        return n


def _reader_readline(self, size: int = -1) -> bytes:  # type: ignore[override]
        line = self.handle.readline(size)
        self.progress.advance(self.task, advance=len(line))
        return line


def _reader_readlines(self, hint: int = -1) -> List[bytes]:
        lines = self.handle.readlines(hint)
        self.progress.advance(self.task, advance=sum(map(len, lines)))
        return lines


def _reader_close(self) -> None:
        if self.close_handle:
            self.handle.close()
        self._closed = True


def _reader_seek(self, offset: int, whence: int = 0) -> int:
        pos = self.handle.seek(offset, whence)
        self.progress.update(self.task, completed=pos)
        return pos


def _reader_tell(self) -> int:
        return self.handle.tell()


def _reader_write(self, s: Any) -> int:
        raise UnsupportedOperation("write")


def _reader_writelines(self, lines: Iterable[Any]) -> None:
        raise UnsupportedOperation("writelines")


def _read_context__init__(self, progress: "Progress", reader: _I) -> None:
        self.progress = progress
        self.reader: _I = reader


def _read_context__enter__(self) -> _I:
        self.progress.start()
        return self.reader.__enter__()


def _read_context__exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.progress.stop()
        self.reader.__exit__(exc_type, exc_val, exc_tb)


def _renderable_column__init__(
        self, renderable: RenderableType = "", *, table_column: Optional[Column] = None
    ):
        self.renderable = renderable
        ProgressColumn.__init__(self, table_column=table_column)


def _renderable_column_render(self, task: "Task") -> RenderableType:
        return self.renderable


def _spinner_column__init__(
        self,
        spinner_name: str = "dots",
        style: Optional[StyleType] = "progress.spinner",
        speed: float = 1.0,
        finished_text: TextType = " ",
        table_column: Optional[Column] = None,
    ):
        self.spinner = Spinner(spinner_name, style=style, speed=speed)
        self.finished_text = (
            Text.from_markup(finished_text)
            if isinstance(finished_text, str)
            else finished_text
        )
        ProgressColumn.__init__(self, table_column=table_column)


def _spinner_column_set_spinner(
        self,
        spinner_name: str,
        spinner_style: Optional[StyleType] = "progress.spinner",
        speed: float = 1.0,
    ) -> None:
        """Set a new spinner.

        Args:
            spinner_name (str): Spinner name, see python -m rich.spinner.
            spinner_style (Optional[StyleType], optional): Spinner style. Defaults to "progress.spinner".
            speed (float, optional): Speed factor of spinner. Defaults to 1.0.
        """
        self.spinner = Spinner(spinner_name, style=spinner_style, speed=speed)


def _spinner_column_render(self, task: "Task") -> RenderableType:
        text = (
            self.finished_text
            if task.finished
            else self.spinner.render(task.get_time())
        )
        return text


def _text_column__init__(
        self,
        text_format: str,
        style: StyleType = "none",
        justify: JustifyMethod = "left",
        markup: bool = True,
        highlighter: Optional[Highlighter] = None,
        table_column: Optional[Column] = None,
    ) -> None:
        self.text_format = text_format
        self.justify: JustifyMethod = justify
        self.style = style
        self.markup = markup
        self.highlighter = highlighter
        ProgressColumn.__init__(self, table_column=table_column or Column(no_wrap=True))


def _text_column_render(self, task: "Task") -> Text:
        _text = self.text_format.format(task=task)
        if self.markup:
            text = Text.from_markup(_text, style=self.style, justify=self.justify)
        else:
            text = Text(_text, style=self.style, justify=self.justify)
        if self.highlighter:
            self.highlighter.highlight(text)
        return text


def _bar_column__init__(
        self,
        bar_width: Optional[int] = 40,
        style: StyleType = "bar.back",
        complete_style: StyleType = "bar.complete",
        finished_style: StyleType = "bar.finished",
        pulse_style: StyleType = "bar.pulse",
        table_column: Optional[Column] = None,
    ) -> None:
        self.bar_width = bar_width
        self.style = style
        self.complete_style = complete_style
        self.finished_style = finished_style
        self.pulse_style = pulse_style
        ProgressColumn.__init__(self, table_column=table_column)


def _bar_column_render(self, task: "Task") -> ProgressBar:
        """Gets a progress bar widget for a task."""
        return ProgressBar(
            total=max(0, task.total) if task.total is not None else None,
            completed=max(0, task.completed),
            width=None if self.bar_width is None else max(1, self.bar_width),
            pulse=not task.started,
            animation_time=task.get_time(),
            style=self.style,
            complete_style=self.complete_style,
            finished_style=self.finished_style,
            pulse_style=self.pulse_style,
        )


def _time_elapsed_column_render(self, task: "Task") -> Text:
        """Show time elapsed."""
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("-:--:--", style="progress.elapsed")
        delta = timedelta(seconds=max(0, int(elapsed)))
        return Text(str(delta), style="progress.elapsed")


def _task_progress_column__init__(
        self,
        text_format: str = "[progress.percentage]{task.percentage:>3.0f}%",
        text_format_no_percentage: str = "",
        style: StyleType = "none",
        justify: JustifyMethod = "left",
        markup: bool = True,
        highlighter: Optional[Highlighter] = None,
        table_column: Optional[Column] = None,
        show_speed: bool = False,
    ) -> None:
        self.text_format_no_percentage = text_format_no_percentage
        self.show_speed = show_speed
        TextColumn.__init__(
            self,
            text_format=text_format,
            style=style,
            justify=justify,
            markup=markup,
            highlighter=highlighter,
            table_column=table_column,
        )


def _task_progress_column_render_speed(cls, speed: Optional[float]) -> Text:
        """Render the speed in iterations per second.

        Args:
            task (Task): A Task object.

        Returns:
            Text: Text object containing the task speed.
        """
        if speed is None:
            return Text("", style="progress.percentage")
        unit, suffix = pick_unit_and_suffix(
            int(speed),
            ["", "×10³", "×10⁶", "×10⁹", "×10¹²"],
            1000,
        )
        data_speed = speed / unit
        return Text(f"{data_speed:.1f}{suffix} it/s", style="progress.percentage")


def _task_progress_column_render(self, task: "Task") -> Text:
        if task.total is None and self.show_speed:
            return self.render_speed(task.finished_speed or task.speed)
        text_format = (
            self.text_format_no_percentage if task.total is None else self.text_format
        )
        _text = text_format.format(task=task)
        if self.markup:
            text = Text.from_markup(_text, style=self.style, justify=self.justify)
        else:
            text = Text(_text, style=self.style, justify=self.justify)
        if self.highlighter:
            self.highlighter.highlight(text)
        return text


def _time_remaining_column__init__(
        self,
        compact: bool = False,
        elapsed_when_finished: bool = False,
        table_column: Optional[Column] = None,
    ):
        self.compact = compact
        self.elapsed_when_finished = elapsed_when_finished
        ProgressColumn.__init__(self, table_column=table_column)


def _time_remaining_column_render(self, task: "Task") -> Text:
        """Show time remaining."""
        if self.elapsed_when_finished and task.finished:
            task_time = task.finished_time
            style = "progress.elapsed"
        else:
            task_time = task.time_remaining
            style = "progress.remaining"

        if task.total is None:
            return Text("", style=style)

        if task_time is None:
            return Text("--:--" if self.compact else "-:--:--", style=style)

        # Based on https://github.com/tqdm/tqdm/blob/master/tqdm/std.py
        minutes, seconds = divmod(int(task_time), 60)
        hours, minutes = divmod(minutes, 60)

        if self.compact and not hours:
            formatted = f"{minutes:02d}:{seconds:02d}"
        else:
            formatted = f"{hours:d}:{minutes:02d}:{seconds:02d}"

        return Text(formatted, style=style)


def _file_size_column_render(self, task: "Task") -> Text:
        """Show data completed."""
        data_size = decimal(int(task.completed))
        return Text(data_size, style="progress.filesize")


def _total_file_size_column_render(self, task: "Task") -> Text:
        """Show data completed."""
        data_size = decimal(int(task.total)) if task.total is not None else ""
        return Text(data_size, style="progress.filesize.total")


def _mof_n_complete_column__init__(self, separator: str = "/", table_column: Optional[Column] = None):
        self.separator = separator
        ProgressColumn.__init__(self, table_column=table_column)


def _mof_n_complete_column_render(self, task: "Task") -> Text:
        """Show completed/total."""
        completed = int(task.completed)
        total = int(task.total) if task.total is not None else "?"
        total_width = len(str(total))
        return Text(
            f"{completed:{total_width}d}{self.separator}{total}",
            style="progress.download",
        )


def _download_column__init__(
        self, binary_units: bool = False, table_column: Optional[Column] = None
    ) -> None:
        self.binary_units = binary_units
        ProgressColumn.__init__(self, table_column=table_column)


def _download_column_render(self, task: "Task") -> Text:
        """Calculate common unit for completed and total."""
        completed = int(task.completed)

        unit_and_suffix_calculation_base = (
            int(task.total) if task.total is not None else completed
        )
        if self.binary_units:
            unit, suffix = pick_unit_and_suffix(
                unit_and_suffix_calculation_base,
                ["bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"],
                1024,
            )
        else:
            unit, suffix = pick_unit_and_suffix(
                unit_and_suffix_calculation_base,
                ["bytes", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"],
                1000,
            )
        precision = 0 if unit == 1 else 1

        completed_ratio = completed / unit
        completed_str = f"{completed_ratio:,.{precision}f}"

        if task.total is not None:
            total = int(task.total)
            total_ratio = total / unit
            total_str = f"{total_ratio:,.{precision}f}"
        else:
            total_str = "?"

        download_status = f"{completed_str}/{total_str} {suffix}"
        download_text = Text(download_status, style="progress.download")
        return download_text


def _transfer_speed_column_render(self, task: "Task") -> Text:
        """Show data transfer speed."""
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("?", style="progress.data.speed")
        data_speed = decimal(int(speed))
        return Text(f"{data_speed}/s", style="progress.data.speed")


def _progress_sample__new__(cls, timestamp: float, completed: float):
    return tuple.__new__(cls, (timestamp, completed))

def _progress_sample_timestamp(self):
    return self[0]

def _progress_sample_completed(self):
    return self[1]


def _task__init__(
    self,
    id: TaskID,
    description: str,
    total: Optional[float],
    completed: float,
    _get_time: GetTimeCallable,
    finished_time: Optional[float] = None,
    visible: bool = True,
    fields: Optional[Dict[str, Any]] = None,
    finished_speed: Optional[float] = None,
    _lock: Optional[RLock] = None,
) -> None:
    self.id = id
    self.description = description
    self.total = total
    self.completed = completed
    self._get_time = _get_time
    self.finished_time = finished_time
    self.visible = visible
    self.fields = fields if fields is not None else {}
    self.finished_speed = finished_speed
    self.start_time = None
    self.stop_time = None
    self._progress: Deque[ProgressSample] = deque(maxlen=1000)
    self._lock = _lock if _lock is not None else RLock()


def _task_get_time(self) -> float:
        """float: Get the current time, in seconds."""
        return self._get_time()


def _task_started(self) -> bool:
        """bool: Check if the task as started."""
        return self.start_time is not None


def _task_remaining(self) -> Optional[float]:
        """Optional[float]: Get the number of steps remaining, if a non-None total was set."""
        if self.total is None:
            return None
        return self.total - self.completed


def _task_elapsed(self) -> Optional[float]:
        """Optional[float]: Time elapsed since task was started, or ``None`` if the task hasn't started."""
        if self.start_time is None:
            return None
        if self.stop_time is not None:
            return self.stop_time - self.start_time
        return self.get_time() - self.start_time


def _task_finished(self) -> bool:
        """Check if the task has finished."""
        return self.finished_time is not None


def _task_percentage(self) -> float:
        """float: Get progress of task as a percentage. If a None total was set, returns 0"""
        if not self.total:
            return 0.0
        completed = (self.completed / self.total) * 100.0
        completed = min(100.0, max(0.0, completed))
        return completed


def _task_speed(self) -> Optional[float]:
        """Optional[float]: Get the estimated speed in steps per second."""
        if self.start_time is None:
            return None
        with self._lock:
            progress = self._progress
            if not progress:
                return None
            total_time = progress[-1].timestamp - progress[0].timestamp
            if total_time == 0:
                return None
            iter_progress = iter(progress)
            next(iter_progress)
            total_completed = sum(sample.completed for sample in iter_progress)
            speed = total_completed / total_time
            return speed


def _task_time_remaining(self) -> Optional[float]:
        """Optional[float]: Get estimated time to completion, or ``None`` if no data."""
        if self.finished:
            return 0.0
        speed = self.speed
        if not speed:
            return None
        remaining = self.remaining
        if remaining is None:
            return None
        estimate = ceil(remaining / speed)
        return estimate


def _task__reset(self) -> None:
        """Reset progress."""
        self._progress.clear()
        self.finished_time = None
        self.finished_speed = None


_Reader = type(
    "_Reader",
    (RawIOBase, BinaryIO),
    {
        "__doc__": "A reader that tracks progress while it's being read from.",
        "__init__": _reader__init__,
        "__enter__": _reader__enter__,
        "__exit__": _reader__exit__,
        "__iter__": _reader__iter__,
        "__next__": _reader__next__,
        "closed": property(_reader_closed),
        "fileno": _reader_fileno,
        "isatty": _reader_isatty,
        "mode": property(_reader_mode),
        "name": property(_reader_name),
        "readable": _reader_readable,
        "seekable": _reader_seekable,
        "writable": _reader_writable,
        "read": _reader_read,
        "readinto": _reader_readinto,
        "readline": _reader_readline,
        "readlines": _reader_readlines,
        "close": _reader_close,
        "seek": _reader_seek,
        "tell": _reader_tell,
        "write": _reader_write,
        "writelines": _reader_writelines
    },
)


_ReadContext = type(
    "_ReadContext",
    (),
    {
        "__doc__": 'A utility class to handle a context for both a reader and a progress.',
        "__init__": _read_context__init__,
        "__enter__": _read_context__enter__,
        "__exit__": _read_context__exit__
    },
)


ProgressSample = type(
    "ProgressSample",
    (tuple,),
    {
        "__doc__": 'Number of steps completed.',
        "__new__": _progress_sample__new__,
        "timestamp": property(_progress_sample_timestamp),
        "completed": property(_progress_sample_completed)
    },
)


Task = type(
    "Task",
    (),
    {
        "get_time": _task_get_time,
        "started": property(_task_started),
        "remaining": property(_task_remaining),
        "elapsed": property(_task_elapsed),
        "finished": property(_task_finished),
        "percentage": property(_task_percentage),
        "speed": property(_task_speed),
        "time_remaining": property(_task_time_remaining),
        "_reset": _task__reset,
        "__init__": _task__init__,
        "__doc__": "Information regarding a progress task.",
    },
)


def wrap_file(
    file: BinaryIO,
    total: int,
    *,
    description: str = "Reading...",
    auto_refresh: bool = True,
    console: Optional[Console] = None,
    transient: bool = False,
    get_time: Optional[Callable[[], float]] = None,
    refresh_per_second: float = 10,
    style: StyleType = "bar.back",
    complete_style: StyleType = "bar.complete",
    finished_style: StyleType = "bar.finished",
    pulse_style: StyleType = "bar.pulse",
    disable: bool = False,
) -> ContextManager[BinaryIO]:
    """Read bytes from a file while tracking progress.

    Args:
        file (Union[str, PathLike[str], BinaryIO]): The path to the file to read, or a file-like object in binary mode.
        total (int): Total number of bytes to read.
        description (str, optional): Description of task show next to progress bar. Defaults to "Reading".
        auto_refresh (bool, optional): Automatic refresh, disable to force a refresh after each iteration. Default is True.
        transient: (bool, optional): Clear the progress on exit. Defaults to False.
        console (Console, optional): Console to write to. Default creates internal Console instance.
        refresh_per_second (float): Number of times per second to refresh the progress information. Defaults to 10.
        style (StyleType, optional): Style for the bar background. Defaults to "bar.back".
        complete_style (StyleType, optional): Style for the completed bar. Defaults to "bar.complete".
        finished_style (StyleType, optional): Style for a finished bar. Defaults to "bar.finished".
        pulse_style (StyleType, optional): Style for pulsing bars. Defaults to "bar.pulse".
        disable (bool, optional): Disable display of progress.
    Returns:
        ContextManager[BinaryIO]: A context manager yielding a progress reader.

    """

    columns: List["ProgressColumn"] = (
        [TextColumn("[progress.description]{task.description}")] if description else []
    )
    columns.extend(
        (
            BarColumn(
                style=style,
                complete_style=complete_style,
                finished_style=finished_style,
                pulse_style=pulse_style,
            ),
            DownloadColumn(),
            TimeRemainingColumn(),
        )
    )
    progress = Progress(
        *columns,
        auto_refresh=auto_refresh,
        console=console,
        transient=transient,
        get_time=get_time,
        refresh_per_second=refresh_per_second or 10,
        disable=disable,
    )

    reader = progress.wrap_file(file, total=total, description=description)
    return _ReadContext(progress, reader)


@typing.overload
def open(
    file: Union[str, "PathLike[str]", bytes],
    mode: Union[Literal["rt"], Literal["r"]],
    buffering: int = -1,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    newline: Optional[str] = None,
    *,
    total: Optional[int] = None,
    description: str = "Reading...",
    auto_refresh: bool = True,
    console: Optional[Console] = None,
    transient: bool = False,
    get_time: Optional[Callable[[], float]] = None,
    refresh_per_second: float = 10,
    style: StyleType = "bar.back",
    complete_style: StyleType = "bar.complete",
    finished_style: StyleType = "bar.finished",
    pulse_style: StyleType = "bar.pulse",
    disable: bool = False,
) -> ContextManager[TextIO]:
    pass


@typing.overload
def open(
    file: Union[str, "PathLike[str]", bytes],
    mode: Literal["rb"],
    buffering: int = -1,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    newline: Optional[str] = None,
    *,
    total: Optional[int] = None,
    description: str = "Reading...",
    auto_refresh: bool = True,
    console: Optional[Console] = None,
    transient: bool = False,
    get_time: Optional[Callable[[], float]] = None,
    refresh_per_second: float = 10,
    style: StyleType = "bar.back",
    complete_style: StyleType = "bar.complete",
    finished_style: StyleType = "bar.finished",
    pulse_style: StyleType = "bar.pulse",
    disable: bool = False,
) -> ContextManager[BinaryIO]:
    pass


def open(
    file: Union[str, "PathLike[str]", bytes],
    mode: Union[Literal["rb"], Literal["rt"], Literal["r"]] = "r",
    buffering: int = -1,
    encoding: Optional[str] = None,
    errors: Optional[str] = None,
    newline: Optional[str] = None,
    *,
    total: Optional[int] = None,
    description: str = "Reading...",
    auto_refresh: bool = True,
    console: Optional[Console] = None,
    transient: bool = False,
    get_time: Optional[Callable[[], float]] = None,
    refresh_per_second: float = 10,
    style: StyleType = "bar.back",
    complete_style: StyleType = "bar.complete",
    finished_style: StyleType = "bar.finished",
    pulse_style: StyleType = "bar.pulse",
    disable: bool = False,
) -> Union[ContextManager[BinaryIO], ContextManager[TextIO]]:
    """Read bytes from a file while tracking progress.

    Args:
        path (Union[str, PathLike[str], BinaryIO]): The path to the file to read, or a file-like object in binary mode.
        mode (str): The mode to use to open the file. Only supports "r", "rb" or "rt".
        buffering (int): The buffering strategy to use, see :func:`io.open`.
        encoding (str, optional): The encoding to use when reading in text mode, see :func:`io.open`.
        errors (str, optional): The error handling strategy for decoding errors, see :func:`io.open`.
        newline (str, optional): The strategy for handling newlines in text mode, see :func:`io.open`
        total: (int, optional): Total number of bytes to read. Must be provided if reading from a file handle. Default for a path is os.stat(file).st_size.
        description (str, optional): Description of task show next to progress bar. Defaults to "Reading".
        auto_refresh (bool, optional): Automatic refresh, disable to force a refresh after each iteration. Default is True.
        transient: (bool, optional): Clear the progress on exit. Defaults to False.
        console (Console, optional): Console to write to. Default creates internal Console instance.
        refresh_per_second (float): Number of times per second to refresh the progress information. Defaults to 10.
        style (StyleType, optional): Style for the bar background. Defaults to "bar.back".
        complete_style (StyleType, optional): Style for the completed bar. Defaults to "bar.complete".
        finished_style (StyleType, optional): Style for a finished bar. Defaults to "bar.finished".
        pulse_style (StyleType, optional): Style for pulsing bars. Defaults to "bar.pulse".
        disable (bool, optional): Disable display of progress.
        encoding (str, optional): The encoding to use when reading in text mode.

    Returns:
        ContextManager[BinaryIO]: A context manager yielding a progress reader.

    """

    columns: List["ProgressColumn"] = (
        [TextColumn("[progress.description]{task.description}")] if description else []
    )
    columns.extend(
        (
            BarColumn(
                style=style,
                complete_style=complete_style,
                finished_style=finished_style,
                pulse_style=pulse_style,
            ),
            DownloadColumn(),
            TimeRemainingColumn(),
        )
    )
    progress = Progress(
        *columns,
        auto_refresh=auto_refresh,
        console=console,
        transient=transient,
        get_time=get_time,
        refresh_per_second=refresh_per_second or 10,
        disable=disable,
    )

    reader = progress.open(
        file,
        mode=mode,
        buffering=buffering,
        encoding=encoding,
        errors=errors,
        newline=newline,
        total=total,
        description=description,
    )
    return _ReadContext(progress, reader)  # type: ignore[return-value, type-var]



def _progress_column_cached_renderable(
    column: "ProgressColumn", task: "Task", current_time: float
) -> Optional[RenderableType]:
    """Return cached renderable if still fresh, else None."""
    if column.max_refresh is None or task.completed:
        return None
    try:
        timestamp, renderable = column._renderable_cache[task.id]
    except KeyError:
        return None
    if timestamp + column.max_refresh > current_time:
        return renderable
    return None


class ProgressColumn(ABC):
    """Base class for a widget to use in progress display."""

    max_refresh: Optional[float] = None

    def __init__(self, table_column: Optional[Column] = None) -> None:
        self._table_column = table_column
        self._renderable_cache: Dict[TaskID, Tuple[float, RenderableType]] = {}
        self._update_time: Optional[float] = None

    def get_table_column(self) -> Column:
        """Get a table column, used to build tasks table."""
        return self._table_column or Column()

    def __call__(self, task: "Task") -> RenderableType:
        """Called by the Progress object to return a renderable for the given task.

        Args:
            task (Task): An object containing information regarding the task.

        Returns:
            RenderableType: Anything renderable (including str).
        """
        current_time = task.get_time()
        cached = _progress_column_cached_renderable(self, task, current_time)
        if cached is not None:
            return cached

        renderable = self.render(task)
        self._renderable_cache[task.id] = (current_time, renderable)
        return renderable

    @abstractmethod
    def render(self, task: "Task") -> RenderableType:
        """Should return a renderable object."""



RenderableColumn = type(
    "RenderableColumn",
    (ProgressColumn,),
    {
        "__doc__": 'A column to insert an arbitrary column.\n\n    Args:\n        renderable (RenderableType, optional): Any renderable. Defaults to empty string.\n    ',
        "__init__": _renderable_column__init__,
        "render": _renderable_column_render
    },
)


SpinnerColumn = type(
    "SpinnerColumn",
    (ProgressColumn,),
    {
        "__doc__": 'A column with a \'spinner\' animation.\n\n    Args:\n        spinner_name (str, optional): Name of spinner animation. Defaults to "dots".\n        style (StyleType, optional): Style of spinner. Defaults to "progress.spinner".\n        speed (float, optional): Speed factor of spinner. Defaults to 1.0.\n        finished_text (TextType, optional): Text used when task is finished. Defaults to " ".\n    ',
        "__init__": _spinner_column__init__,
        "set_spinner": _spinner_column_set_spinner,
        "render": _spinner_column_render
    },
)


TextColumn = type(
    "TextColumn",
    (ProgressColumn,),
    {
        "__doc__": 'A column containing text.',
        "__init__": _text_column__init__,
        "render": _text_column_render
    },
)


BarColumn = type(
    "BarColumn",
    (ProgressColumn,),
    {
        "__doc__": 'Renders a visual progress bar.\n\n    Args:\n        bar_width (Optional[int], optional): Width of bar or None for full width. Defaults to 40.\n        style (StyleType, optional): Style for the bar background. Defaults to "bar.back".\n        complete_style (StyleType, optional): Style for the completed bar. Defaults to "bar.complete".\n        finished_style (StyleType, optional): Style for a finished bar. Defaults to "bar.finished".\n        pulse_style (StyleType, optional): Style for pulsing bars. Defaults to "bar.pulse".\n    ',
        "__init__": _bar_column__init__,
        "render": _bar_column_render
    },
)


TimeElapsedColumn = type(
    "TimeElapsedColumn",
    (ProgressColumn,),
    {
        "__doc__": 'Renders time elapsed.',
        "render": _time_elapsed_column_render
    },
)


TaskProgressColumn = type(
    "TaskProgressColumn",
    (TextColumn,),
    {
        "__doc__": 'Show task progress as a percentage.\n\n    Args:\n        text_format (str, optional): Format for percentage display. Defaults to "[progress.percentage]{task.percentage:>3.0f}%".\n        text_format_no_percentage (str, optional): Format if percentage is unknown. Defaults to "".\n        style (StyleType, optional): Style of output. Defaults to "none".\n        justify (JustifyMethod, optional): Text justification. Defaults to "left".\n        markup (bool, optional): Enable markup. Defaults to True.\n        highlighter (Optional[Highlighter], optional): Highlighter to apply to output. Defaults to None.\n        table_column (Optional[Column], optional): Table Column to use. Defaults to None.\n        show_speed (bool, optional): Show speed if total is unknown. Defaults to False.\n    ',
        "__init__": _task_progress_column__init__,
        "render_speed": classmethod(_task_progress_column_render_speed),
        "render": _task_progress_column_render
    },
)


TimeRemainingColumn = type(
    "TimeRemainingColumn",
    (ProgressColumn,),
    {
        "__doc__": 'Renders estimated time remaining.\n\n    Args:\n        compact (bool, optional): Render MM:SS when time remaining is less than an hour. Defaults to False.\n        elapsed_when_finished (bool, optional): Render time elapsed when the task is finished. Defaults to False.\n    ',
        "max_refresh": 0.5,
        "__init__": _time_remaining_column__init__,
        "render": _time_remaining_column_render
    },
)


FileSizeColumn = type(
    "FileSizeColumn",
    (ProgressColumn,),
    {
        "__doc__": 'Renders completed filesize.',
        "render": _file_size_column_render
    },
)


TotalFileSizeColumn = type(
    "TotalFileSizeColumn",
    (ProgressColumn,),
    {
        "__doc__": 'Renders total filesize.',
        "render": _total_file_size_column_render
    },
)


MofNCompleteColumn = type(
    "MofNCompleteColumn",
    (ProgressColumn,),
    {
        "__doc__": 'Renders completed count/total, e.g. \'  10/1000\'.\n\n    Best for bounded tasks with int quantities.\n\n    Space pads the completed count so that progress length does not change as task progresses\n    past powers of 10.\n\n    Args:\n        separator (str, optional): Text to separate completed and total values. Defaults to "/".\n    ',
        "__init__": _mof_n_complete_column__init__,
        "render": _mof_n_complete_column_render
    },
)


DownloadColumn = type(
    "DownloadColumn",
    (ProgressColumn,),
    {
        "__doc__": "Renders file size downloaded and total, e.g. '0.5/2.3 GB'.\n\n    Args:\n        binary_units (bool, optional): Use binary units, KiB, MiB etc. Defaults to False.\n    ",
        "__init__": _download_column__init__,
        "render": _download_column_render
    },
)


TransferSpeedColumn = type(
    "TransferSpeedColumn",
    (ProgressColumn,),
    {
        "__doc__": 'Renders human readable transfer speed.',
        "render": _transfer_speed_column_render
    },
)

def _normalize_progress_open_buffering(
    mode: str, buffering: int
) -> tuple[str, int, bool]:
    """Normalize mode and buffering for Progress.open."""
    _mode = "".join(sorted(mode, reverse=False))
    if _mode not in ("br", "rt", "r"):
        raise ValueError(f"invalid mode {mode!r}")

    line_buffering = buffering == 1
    if _mode == "br" and buffering == 1:
        warnings.warn(
            "line buffering (buffering=1) isn't supported in binary mode, the default buffer size will be used",
            RuntimeWarning,
        )
        buffering = -1
    elif _mode in ("rt", "r"):
        if buffering == 0:
            raise ValueError("can't have unbuffered text I/O")
        if buffering == 1:
            buffering = -1
    return _mode, buffering, line_buffering


def _progress_update_speed_samples(
    task: "Task",
    update_completed: float,
    current_time: float,
    speed_estimate_period: float,
) -> None:
    """Update speed samples and finished time for a task."""
    old_sample_time = current_time - speed_estimate_period
    _progress = task._progress
    popleft = _progress.popleft
    while _progress and _progress[0].timestamp < old_sample_time:
        popleft()
    if update_completed > 0:
        _progress.append(ProgressSample(current_time, update_completed))
    if (
        task.total is not None
        and task.completed >= task.total
        and task.finished_time is None
    ):
        task.finished_time = task.elapsed


class Progress(JupyterMixin):
    """Renders an auto-updating progress bar(s).

    Args:
        console (Console, optional): Optional Console instance. Defaults to an internal Console instance writing to stdout.
        auto_refresh (bool, optional): Enable auto refresh. If disabled, you will need to call `refresh()`.
        refresh_per_second (float, optional): Number of times per second to refresh the progress information. Defaults to 10.
        speed_estimate_period: (float, optional): Period (in seconds) used to calculate the speed estimate. Defaults to 30.
        transient: (bool, optional): Clear the progress on exit. Defaults to False.
        redirect_stdout: (bool, optional): Enable redirection of stdout, so ``print`` may be used. Defaults to True.
        redirect_stderr: (bool, optional): Enable redirection of stderr. Defaults to True.
        get_time: (Callable, optional): A callable that gets the current time, or None to use Console.get_time. Defaults to None.
        disable (bool, optional): Disable progress display. Defaults to False
        expand (bool, optional): Expand tasks table to fit width. Defaults to False.
    """

    def __init__(
        self,
        *columns: Union[str, ProgressColumn],
        console: Optional[Console] = None,
        auto_refresh: bool = True,
        refresh_per_second: float = 10,
        speed_estimate_period: float = 30.0,
        transient: bool = False,
        redirect_stdout: bool = True,
        redirect_stderr: bool = True,
        get_time: Optional[GetTimeCallable] = None,
        disable: bool = False,
        expand: bool = False,
    ) -> None:
        assert refresh_per_second > 0, "refresh_per_second must be > 0"
        self._lock = RLock()
        self.columns = columns or self.get_default_columns()
        self.speed_estimate_period = speed_estimate_period

        self.disable = disable
        self.expand = expand
        self._tasks: Dict[TaskID, Task] = {}
        self._task_index: TaskID = TaskID(0)
        self.live = Live(
            console=console or get_console(),
            auto_refresh=auto_refresh,
            refresh_per_second=refresh_per_second,
            transient=transient,
            redirect_stdout=redirect_stdout,
            redirect_stderr=redirect_stderr,
            get_renderable=self.get_renderable,
        )
        self.get_time = get_time or self.console.get_time
        self.print = self.console.print
        self.log = self.console.log

    @classmethod
    def get_default_columns(cls) -> Tuple[ProgressColumn, ...]:
        """Get the default columns used for a new Progress instance:
           - a text column for the description (TextColumn)
           - the bar itself (BarColumn)
           - a text column showing completion percentage (TextColumn)
           - an estimated-time-remaining column (TimeRemainingColumn)
        If the Progress instance is created without passing a columns argument,
        the default columns defined here will be used.

        You can also create a Progress instance using custom columns before
        and/or after the defaults, as in this example:

            progress = Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                "Elapsed:",
                TimeElapsedColumn(),
            )

        This code shows the creation of a Progress display, containing
        a spinner to the left, the default columns, and a labeled elapsed
        time column.
        """
        return (
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
        )

    @property
    def console(self) -> Console:
        return self.live.console

    @property
    def tasks(self) -> List[Task]:
        """Get a list of Task instances."""
        with self._lock:
            return list(self._tasks.values())

    @property
    def task_ids(self) -> List[TaskID]:
        """A list of task IDs."""
        with self._lock:
            return list(self._tasks.keys())

    @property
    def finished(self) -> bool:
        """Check if all tasks have been completed."""
        with self._lock:
            if not self._tasks:
                return True
            return all(task.finished for task in self._tasks.values())

    def start(self) -> None:
        """Start the progress display."""
        if not self.disable:
            self.live.start(refresh=True)

    def stop(self) -> None:
        """Stop the progress display."""
        if not self.disable:
            self.live.stop()
            if not self.console.is_interactive and not self.console.is_jupyter:
                self.console.print()

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.stop()

    def track(
        self,
        sequence: Iterable[ProgressType],
        total: Optional[float] = None,
        completed: int = 0,
        task_id: Optional[TaskID] = None,
        description: str = "Working...",
        update_period: float = 0.1,
    ) -> Iterable[ProgressType]:
        """Track progress by iterating over a sequence.

        You can also track progress of an iterable, which might require that you additionally specify ``total``.

        Args:
            sequence (Iterable[ProgressType]): Values you want to iterate over and track progress.
            total: (float, optional): Total number of steps. Default is len(sequence).
            completed (int, optional): Number of steps completed so far. Defaults to 0.
            task_id: (TaskID): Task to track. Default is new task.
            description: (str, optional): Description of task, if new task is created.
            update_period (float, optional): Minimum time (in seconds) between calls to update(). Defaults to 0.1.

        Returns:
            Iterable[ProgressType]: An iterable of values taken from the provided sequence.
        """
        if total is None:
            total = float(length_hint(sequence)) or None

        if task_id is None:
            task_id = self.add_task(description, total=total, completed=completed)
        else:
            self.update(task_id, total=total, completed=completed)

        if self.live.auto_refresh:
            with _TrackThread(self, task_id, update_period) as track_thread:
                for value in sequence:
                    yield value
                    track_thread.completed += 1
        else:
            advance = self.advance
            refresh = self.refresh
            for value in sequence:
                yield value
                advance(task_id, 1)
                refresh()

    def wrap_file(
        self,
        file: BinaryIO,
        total: Optional[int] = None,
        *,
        task_id: Optional[TaskID] = None,
        description: str = "Reading...",
    ) -> BinaryIO:
        """Track progress file reading from a binary file.

        Args:
            file (BinaryIO): A file-like object opened in binary mode.
            total (int, optional): Total number of bytes to read. This must be provided unless a task with a total is also given.
            task_id (TaskID): Task to track. Default is new task.
            description (str, optional): Description of task, if new task is created.

        Returns:
            BinaryIO: A readable file-like object in binary mode.

        Raises:
            ValueError: When no total value can be extracted from the arguments or the task.
        """
        # attempt to recover the total from the task
        total_bytes: Optional[float] = None
        if total is not None:
            total_bytes = total
        elif task_id is not None:
            with self._lock:
                total_bytes = self._tasks[task_id].total
        if total_bytes is None:
            raise ValueError(
                "unable to get the total number of bytes, please specify 'total'"
            )

        # update total of task or create new task
        if task_id is None:
            task_id = self.add_task(description, total=total_bytes)
        else:
            self.update(task_id, total=total_bytes)

        return _Reader(file, self, task_id, close_handle=False)

    @typing.overload
    def open(
        self,
        file: Union[str, "PathLike[str]", bytes],
        mode: Literal["rb"],
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        *,
        total: Optional[int] = None,
        task_id: Optional[TaskID] = None,
        description: str = "Reading...",
    ) -> BinaryIO:
        pass

    @typing.overload
    def open(
        self,
        file: Union[str, "PathLike[str]", bytes],
        mode: Union[Literal["r"], Literal["rt"]],
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        *,
        total: Optional[int] = None,
        task_id: Optional[TaskID] = None,
        description: str = "Reading...",
    ) -> TextIO:
        pass

    def open(
        self,
        file: Union[str, "PathLike[str]", bytes],
        mode: Union[Literal["rb"], Literal["rt"], Literal["r"]] = "r",
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        *,
        total: Optional[int] = None,
        task_id: Optional[TaskID] = None,
        description: str = "Reading...",
    ) -> Union[BinaryIO, TextIO]:
        """Track progress while reading from a binary file.

        Args:
            path (Union[str, PathLike[str]]): The path to the file to read.
            mode (str): The mode to use to open the file. Only supports "r", "rb" or "rt".
            buffering (int): The buffering strategy to use, see :func:`io.open`.
            encoding (str, optional): The encoding to use when reading in text mode, see :func:`io.open`.
            errors (str, optional): The error handling strategy for decoding errors, see :func:`io.open`.
            newline (str, optional): The strategy for handling newlines in text mode, see :func:`io.open`.
            total (int, optional): Total number of bytes to read. If none given, os.stat(path).st_size is used.
            task_id (TaskID): Task to track. Default is new task.
            description (str, optional): Description of task, if new task is created.

        Returns:
            BinaryIO: A readable file-like object in binary mode.

        Raises:
            ValueError: When an invalid mode is given.
        """
        _mode, buffering, line_buffering = _normalize_progress_open_buffering(
            mode, buffering
        )

        # attempt to get the total with `os.stat`
        if total is None:
            total = stat(file).st_size

        # update total of task or create new task
        if task_id is None:
            task_id = self.add_task(description, total=total)
        else:
            self.update(task_id, total=total)

        # open the file in binary mode,
        handle = io.open(file, "rb", buffering=buffering)
        reader = _Reader(handle, self, task_id, close_handle=True)

        # wrap the reader in a `TextIOWrapper` if text mode
        if mode in ("r", "rt"):
            return io.TextIOWrapper(
                reader,
                encoding=encoding,
                errors=errors,
                newline=newline,
                line_buffering=line_buffering,
            )

        return reader

    def start_task(self, task_id: TaskID) -> None:
        """Start a task.

        Starts a task (used when calculating elapsed time). You may need to call this manually,
        if you called ``add_task`` with ``start=False``.

        Args:
            task_id (TaskID): ID of task.
        """
        with self._lock:
            task = self._tasks[task_id]
            if task.start_time is None:
                task.start_time = self.get_time()

    def stop_task(self, task_id: TaskID) -> None:
        """Stop a task.

        This will freeze the elapsed time on the task.

        Args:
            task_id (TaskID): ID of task.
        """
        with self._lock:
            task = self._tasks[task_id]
            current_time = self.get_time()
            if task.start_time is None:
                task.start_time = current_time
            task.stop_time = current_time

    def update(
        self,
        task_id: TaskID,
        *,
        total: Optional[float] = None,
        completed: Optional[float] = None,
        advance: Optional[float] = None,
        description: Optional[str] = None,
        visible: Optional[bool] = None,
        refresh: bool = False,
        **fields: Any,
    ) -> None:
        """Update information associated with a task.

        Args:
            task_id (TaskID): Task id (returned by add_task).
            total (float, optional): Updates task.total if not None.
            completed (float, optional): Updates task.completed if not None.
            advance (float, optional): Add a value to task.completed if not None.
            description (str, optional): Change task description if not None.
            visible (bool, optional): Set visible flag if not None.
            refresh (bool): Force a refresh of progress information. Default is False.
            **fields (Any): Additional data fields required for rendering.
        """
        with self._lock:
            task = self._tasks[task_id]
            completed_start = task.completed

            if total is not None and total != task.total:
                task.total = total
                task._reset()
            if advance is not None:
                task.completed += advance
            if completed is not None:
                task.completed = completed
            if description is not None:
                task.description = description
            if visible is not None:
                task.visible = visible
            task.fields.update(fields)
            update_completed = task.completed - completed_start
            _progress_update_speed_samples(
                task, update_completed, self.get_time(), self.speed_estimate_period
            )

        if refresh:
            self.refresh()

    def reset(
        self,
        task_id: TaskID,
        *,
        start: bool = True,
        total: Optional[float] = None,
        completed: int = 0,
        visible: Optional[bool] = None,
        description: Optional[str] = None,
        **fields: Any,
    ) -> None:
        """Reset a task so completed is 0 and the clock is reset.

        Args:
            task_id (TaskID): ID of task.
            start (bool, optional): Start the task after reset. Defaults to True.
            total (float, optional): New total steps in task, or None to use current total. Defaults to None.
            completed (int, optional): Number of steps completed. Defaults to 0.
            visible (bool, optional): Set visible flag if not None.
            description (str, optional): Change task description if not None. Defaults to None.
            **fields (str): Additional data fields required for rendering.
        """
        current_time = self.get_time()
        with self._lock:
            task = self._tasks[task_id]
            task._reset()
            task.start_time = current_time if start else None
            if total is not None:
                task.total = total
            task.completed = completed
            if visible is not None:
                task.visible = visible
            if fields:
                task.fields = fields
            if description is not None:
                task.description = description
            task.finished_time = None
        self.refresh()

    def advance(self, task_id: TaskID, advance: float = 1) -> None:
        """Advance task by a number of steps.

        Args:
            task_id (TaskID): ID of task.
            advance (float): Number of steps to advance. Default is 1.
        """
        current_time = self.get_time()
        with self._lock:
            task = self._tasks[task_id]
            completed_start = task.completed
            task.completed += advance
            update_completed = task.completed - completed_start
            old_sample_time = current_time - self.speed_estimate_period
            _progress = task._progress

            popleft = _progress.popleft
            while _progress and _progress[0].timestamp < old_sample_time:
                popleft()
            while len(_progress) > 1000:
                popleft()
            _progress.append(ProgressSample(current_time, update_completed))
            if (
                task.total is not None
                and task.completed >= task.total
                and task.finished_time is None
            ):
                task.finished_time = task.elapsed
                task.finished_speed = task.speed

    def refresh(self) -> None:
        """Refresh (render) the progress information."""
        if not self.disable and self.live.is_started:
            self.live.refresh()

    def get_renderable(self) -> RenderableType:
        """Get a renderable for the progress display."""
        renderable = Group(*self.get_renderables())
        return renderable

    def get_renderables(self) -> Iterable[RenderableType]:
        """Get a number of renderables for the progress display."""
        table = self.make_tasks_table(self.tasks)
        yield table

    def make_tasks_table(self, tasks: Iterable[Task]) -> Table:
        """Get a table to render the Progress display.

        Args:
            tasks (Iterable[Task]): An iterable of Task instances, one per row of the table.

        Returns:
            Table: A table instance.
        """
        table_columns = (
            (
                Column(no_wrap=True)
                if isinstance(_column, str)
                else _column.get_table_column().copy()
            )
            for _column in self.columns
        )
        table = Table.grid(*table_columns, padding=(0, 1), expand=self.expand)

        for task in tasks:
            if task.visible:
                table.add_row(
                    *(
                        (
                            column.format(task=task)
                            if isinstance(column, str)
                            else column(task)
                        )
                        for column in self.columns
                    )
                )
        return table

    def __rich__(self) -> RenderableType:
        """Makes the Progress class itself renderable."""
        with self._lock:
            return self.get_renderable()

    def add_task(
        self,
        description: str,
        start: bool = True,
        total: Optional[float] = 100.0,
        completed: int = 0,
        visible: bool = True,
        **fields: Any,
    ) -> TaskID:
        """Add a new 'task' to the Progress display.

        Args:
            description (str): A description of the task.
            start (bool, optional): Start the task immediately (to calculate elapsed time). If set to False,
                you will need to call `start` manually. Defaults to True.
            total (float, optional): Number of total steps in the progress if known.
                Set to None to render a pulsing animation. Defaults to 100.
            completed (int, optional): Number of steps completed so far. Defaults to 0.
            visible (bool, optional): Enable display of the task. Defaults to True.
            **fields (str): Additional data fields required for rendering.

        Returns:
            TaskID: An ID you can use when calling `update`.
        """
        with self._lock:
            task = Task(
                self._task_index,
                description,
                total,
                completed,
                visible=visible,
                fields=fields,
                _get_time=self.get_time,
                _lock=self._lock,
            )
            self._tasks[self._task_index] = task
            if start:
                self.start_task(self._task_index)
            new_task_index = self._task_index
            self._task_index = TaskID(int(self._task_index) + 1)
        self.refresh()
        return new_task_index

    def remove_task(self, task_id: TaskID) -> None:
        """Delete a task if it exists.

        Args:
            task_id (TaskID): A task ID.

        """
        with self._lock:
            del self._tasks[task_id]


if __name__ == "__main__":  # pragma: no coverage
    import random
    import time

    from .panel import Panel
    from .rule import Rule
    from .syntax import Syntax
    from .table import Table

    syntax = Syntax(
        '''def loop_last(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    for value in iter_values:
        yield False, previous_value
        previous_value = value
    yield True, previous_value''',
        "python",
        line_numbers=True,
    )

    table = Table("foo", "bar", "baz")
    table.add_row("1", "2", "3")

    progress_renderables = [
        "Text may be printed while the progress bars are rendering.",
        Panel("In fact, [i]any[/i] renderable will work"),
        "Such as [magenta]tables[/]...",
        table,
        "Pretty printed structures...",
        {"type": "example", "text": "Pretty printed"},
        "Syntax...",
        syntax,
        Rule("Give it a try!"),
    ]

    from itertools import cycle

    examples = cycle(progress_renderables)

    console = Console(record=True)

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        task1 = progress.add_task("[red]Downloading", total=1000)
        task2 = progress.add_task("[green]Processing", total=1000)
        task3 = progress.add_task("[yellow]Thinking", total=None)

        while not progress.finished:
            progress.update(task1, advance=0.5)
            progress.update(task2, advance=0.3)
            time.sleep(0.01)
            if random.randint(0, 100) < 1:
                progress.log(next(examples))
