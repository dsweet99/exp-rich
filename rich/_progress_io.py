"""Progress.open / Progress.update helpers (extracted for kiss)."""
from __future__ import annotations

import io
import importlib as _importlib
import warnings
from os import PathLike, stat
from typing import Any, BinaryIO, Literal, Optional, TextIO, Union

TaskID = _importlib.import_module("._progress_types", __package__).TaskID
ProgressSample = _importlib.import_module("._progress_types", __package__).ProgressSample


def normalize_open_mode(
    mode: Union[Literal["rb"], Literal["rt"], Literal["r"]], buffering: int
) -> tuple[str, int, bool]:
    """Return (normalized_mode, buffering, line_buffering) for progress.open."""
    _mode = "".join(sorted(mode, reverse=False))
    if _mode not in ("br", "rt", "r"):
        raise ValueError(f"invalid mode {mode!r}")
    line_buffering = buffering == 1
    if _mode == "br" and buffering == 1:
        warnings.warn(
            "line buffering (buffering=1) isn't supported in binary mode, "
            "the default buffer size will be used",
            RuntimeWarning,
        )
        buffering = -1
    elif _mode in ("rt", "r"):
        if buffering == 0:
            raise ValueError("can't have unbuffered text I/O")
        if buffering == 1:
            buffering = -1
    return _mode, buffering, line_buffering


def progress_open_file(
    progress: Any,
    file: Union[str, "PathLike[str]", bytes],
    mode: Union[Literal["rb"], Literal["rt"], Literal["r"]],
    buffering: int,
    encoding: Optional[str],
    errors: Optional[str],
    newline: Optional[str],
    *,
    total: Optional[int],
    task_id: Optional[TaskID],
    description: str,
) -> Union[BinaryIO, TextIO]:
    """Open a file and track read progress."""
    _mode, buffering, line_buffering = normalize_open_mode(mode, buffering)
    if total is None:
        total = stat(file).st_size
    if task_id is None:
        task_id = progress.add_task(description, total=total)
    else:
        progress.update(task_id, total=total)
    handle = io.open(file, "rb", buffering=buffering)
    _Reader = _importlib.import_module("._progress_types", __package__)._Reader
    reader = _Reader(handle, progress, task_id, close_handle=True)
    if mode in ("r", "rt"):
        return io.TextIOWrapper(
            reader,
            encoding=encoding,
            errors=errors,
            newline=newline,
            line_buffering=line_buffering,
        )
    return reader


def apply_task_update(
    task: Any,
    *,
    total: Optional[float],
    completed: Optional[float],
    advance: Optional[float],
    description: Optional[str],
    visible: Optional[bool],
    fields: dict[str, Any],
    get_time: Any,
    speed_estimate_period: float,
    progress_sample_class: type,
) -> None:
    """Apply field updates and refresh speed samples for one task."""
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
    current_time = get_time()
    old_sample_time = current_time - speed_estimate_period
    samples = task._progress
    popleft = samples.popleft
    while samples and samples[0].timestamp < old_sample_time:
        popleft()
    if update_completed > 0:
        samples.append(progress_sample_class(current_time, update_completed))
    if (
        task.total is not None
        and task.completed >= task.total
        and task.finished_time is None
    ):
        task.finished_time = task.elapsed
