"""Unit tests for Rich example scripts."""

import io
import os
import pathlib
import signal
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console
from rich.text import Text

from examples.attrs import Model, Point3D, Triangle
from examples.columns import get_content
from examples.downloader import copy_url, download, handle_sigint
from examples.dynamic_progress import run_steps
from examples.exception import divide_all, divide_by
from examples.export import print_table
from examples.fullscreen import Header, make_layout, make_sponsor_message, make_syntax
from examples.group2 import get_panels
from examples.highlighter import EmailHighlighter
from examples.layout import Clock
from examples.listdir import make_filename_text
from examples.log import RequestHighlighter
from examples.print_calendar import print_calendar
from examples.rainbow import RainbowHighlighter
from examples.recursive_error import recursive_bar, recursive_foo
import examples.recursive_error as recursive_error
from examples.suppress import hello
from examples.table_movie import beat
from examples.top_lite_simulator import (
    Process,
    create_process_table,
    generate_process,
)
from examples.tree import walk_directory


def test_attrs_models():
    point = Point3D(x=1.0, y=2.0, z=3.0)
    triangle = Triangle(point1=point, point2=point, point3=point)
    model = Model(name="demo", triangles=[triangle])
    assert model.name == "demo"
    assert len(model.triangles) == 1


def test_columns_get_content():
    user = {
        "name": {"first": "Ada", "last": "Lovelace"},
        "location": {"country": "UK"},
    }
    content = get_content(user)
    assert "Ada Lovelace" in content
    assert "UK" in content


def test_downloader_copy_url(tmp_path):
    response = MagicMock()
    response.info.return_value = {"Content-length": "4"}
    response.read.side_effect = [b"data", b""]

    with patch("examples.downloader.urlopen", return_value=response):
        with patch("examples.downloader.progress") as progress:
            progress.console.log = MagicMock()
            progress.update = MagicMock()
            progress.start_task = MagicMock()
            task_id = progress.add_task.return_value
            copy_url(task_id, "http://example.com/file.txt", str(tmp_path / "f.txt"))

    assert (tmp_path / "f.txt").read_bytes() == b"data"


def test_downloader_download_and_sigint():
    from examples.downloader import done_event

    done_event.clear()
    handle_sigint(signal.SIGINT, None)
    with patch("examples.downloader.copy_url"):
        with patch("examples.downloader.progress") as progress:
            progress.__enter__ = MagicMock(return_value=progress)
            progress.__exit__ = MagicMock(return_value=False)
            progress.add_task.return_value = 1
            download(["http://example.com/a"], "/tmp")


def test_dynamic_progress_run_steps():
    with patch("examples.dynamic_progress.time.sleep"):
        with patch("examples.dynamic_progress.step_progress") as step_progress:
            with patch("examples.dynamic_progress.app_steps_progress") as app_steps:
                step_progress.add_task.return_value = 1
                app_steps.add_task.return_value = 2
                run_steps("demo", (1, 1), 2)
                assert step_progress.update.called
                assert app_steps.update.called


def test_exception_helpers():
    assert divide_by(10, 2) == 5
    console = Console(file=io.StringIO())
    with patch("examples.exception.console", console):
        divide_all([(1, 1), (1, 0)])
    assert console.file.getvalue()


def test_export_print_table():
    with patch("examples.export.console") as console:
        print_table()
        assert console.print.called


def test_fullscreen_helpers():
    layout = make_layout()
    assert layout.name == "root"
    panel = make_sponsor_message()
    assert panel.renderable is not None
    header = Header().__rich__()
    assert header.renderable is not None
    assert "ratio_resolve" in make_syntax().code


def test_group2_panels():
    from rich.console import Group

    panels = get_panels()
    assert isinstance(panels, Group)


def test_email_highlighter():
    highlighter = EmailHighlighter()
    text = Text("mail@example.com")
    highlighter.highlight(text)
    assert text.spans


def test_layout_clock():
    clock = Clock()
    rendered = clock.__rich__()
    assert str(datetime.now().year) in str(rendered)


def test_listdir_make_filename_text(tmp_path):
    (tmp_path / "notes.txt").write_text("x")
    text = make_filename_text("notes.txt", str(tmp_path))
    assert "notes.txt" in str(text)


def test_request_highlighter():
    highlighter = RequestHighlighter()
    text = Text("HTTP GET /index.html 200 [0.1, 127.0.0.1:1]")
    highlighter.highlight(text)
    assert text.spans


def test_print_calendar():
    console = Console(file=io.StringIO(), width=200)
    with patch("examples.print_calendar.Console", return_value=console):
        print_calendar(2020)
    output = console.file.getvalue()
    assert "2020" in output
    assert "January" in output


def test_rainbow_highlighter():
    highlighter = RainbowHighlighter()
    text = Text("hello")
    highlighter.highlight(text)
    assert len(text.spans) == len("hello")


def test_recursive_error_functions():
    assert recursive_error.recursive_foo is recursive_foo
    assert recursive_error.recursive_bar is recursive_bar
    with pytest.raises(RecursionError):
        recursive_foo(1)
    with pytest.raises(RecursionError):
        recursive_bar(1)
    with pytest.raises(RecursionError):
        recursive_error.recursive_foo(1)


def test_suppress_hello():
    from click.testing import CliRunner

    runner = CliRunner()
    with pytest.raises(ZeroDivisionError):
        runner.invoke(hello, ["--count", "1"], catch_exceptions=False)


def test_table_movie_beat():
    with patch("examples.table_movie.time.sleep") as sleep:
        with beat(2):
            pass
        sleep.assert_called_once()


def test_top_lite_simulator():
    process = generate_process(42)
    assert process.pid == 42
    assert process.memory_str
    assert process.time_str
    table = create_process_table(3)
    assert table.row_count == 3


def test_process_properties():
    process = Process(
        pid=1,
        command="demo",
        cpu_percent=1.0,
        memory=500,
        start_time=datetime.now(),
        thread_count=1,
        state="running",
    )
    assert process.memory_str == "500"
    assert process.time_str.startswith("0:")
    assert Process.memory_str is not None
    assert Process.time_str is not None


def test_walk_directory(tmp_path):
    (tmp_path / "a.txt").write_text("x")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("y")

    from rich.tree import Tree

    tree = Tree("root")
    walk_directory(pathlib.Path(tmp_path), tree)
    assert tree.children


def test_rainbow_highlight_method():
    highlighter = RainbowHighlighter()
    text = Text("abc")
    RainbowHighlighter.highlight(highlighter, text)
    assert text.spans
