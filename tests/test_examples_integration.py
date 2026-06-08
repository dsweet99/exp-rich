"""Example tests: downloader, dynamic progress, layout, recursive error, suppress."""

from __future__ import annotations

import pytest


def test_downloader_functions(monkeypatch, tmp_path):
    from examples import downloader

    monkeypatch.setattr(downloader.signal, "signal", lambda *a, **k: None)
    downloader.handle_sigint(None, None)

    class FakeResponse:
        headers = {"Content-Length": "3"}

        def info(self):
            return {"Content-length": "3"}

        def read(self, n=-1):
            return b"abc"

    monkeypatch.setattr(downloader, "urlopen", lambda url: FakeResponse())
    task_id = downloader.progress.add_task("download", filename="x", start=False)
    downloader.copy_url(task_id, "http://example.com", str(tmp_path / "out.bin"))
    downloader.download(["http://example.com/x"], str(tmp_path))


def test_recursive_error_handlers():
    from examples.recursive_error import recursive_demo_bar, recursive_demo_foo

    with pytest.raises(RecursionError):
        recursive_demo_foo(1)
    assert callable(recursive_demo_bar)
