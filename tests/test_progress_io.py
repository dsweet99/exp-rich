"""Unit tests for progress I/O helpers."""
from __future__ import annotations

import importlib as _importlib
from types import SimpleNamespace

import pytest

_progress_io = _importlib.import_module("rich._progress_io")
ProgressSample = _importlib.import_module("rich._progress_types").ProgressSample


def test_normalize_open_mode_text():
    mode, buffering, line_buffering = _progress_io.normalize_open_mode("r", 1)
    assert mode == "r"
    assert buffering == -1
    assert line_buffering is True


def test_normalize_open_mode_binary_rejects_line_buffering():
    mode, buffering, line_buffering = _progress_io.normalize_open_mode("rb", -1)
    assert mode == "br"
    assert buffering == -1
    assert line_buffering is False


def test_normalize_open_mode_invalid():
    with pytest.raises(ValueError, match="invalid mode"):
        _progress_io.normalize_open_mode("w", -1)  # type: ignore[arg-type]


def test_normalize_open_mode_unbuffered_text_fails():
    with pytest.raises(ValueError, match="unbuffered"):
        _progress_io.normalize_open_mode("rt", 0)


def test_apply_task_update_advances_and_samples():
    task = SimpleNamespace(
        total=10.0,
        completed=0.0,
        description="work",
        visible=True,
        fields={},
        finished_time=None,
        elapsed=1.0,
        _progress=__import__("collections").deque(),
        _reset=lambda: None,
    )

    _progress_io.apply_task_update(
        task,
        total=None,
        completed=None,
        advance=2.0,
        description="done",
        visible=False,
        fields={"key": "val"},
        get_time=lambda: 100.0,
        speed_estimate_period=0.5,
        progress_sample_class=ProgressSample,
    )

    assert task.completed == 2.0
    assert task.description == "done"
    assert task.visible is False
    assert task.fields == {"key": "val"}
    assert len(task._progress) == 1


def test_progress_open_file_tracks_bytes(tmp_path):
    Progress = _importlib.import_module("rich.progress").Progress

    data_file = tmp_path / "data.bin"
    data_file.write_bytes(b"hello")

    progress = Progress()
    with progress:
        handle = _progress_io.progress_open_file(
            progress,
            str(data_file),
            "rb",
            -1,
            None,
            None,
            None,
            total=None,
            task_id=None,
            description="read",
        )
        assert handle.read() == b"hello"
        handle.close()

    tasks = list(progress.tasks)
    assert len(tasks) == 1
    assert tasks[0].total == 5
