"""Exercise progress-related example scripts."""

from __future__ import annotations


def test_jobs_progress_symbols():
    from examples import jobs

    assert jobs.JOBS
    assert jobs.progress is not None


def test_cp_progress_progress_class():
    from examples import cp_progress

    assert cp_progress.Progress is not None


def test_file_progress_wrap_file():
    from examples import file_progress

    assert file_progress.wrap_file is not None


def test_live_progress_symbols():
    from examples import live_progress

    assert live_progress.Progress is not None
    assert live_progress.Live is not None
