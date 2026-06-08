"""Example test: dynamic progress demo."""

from __future__ import annotations


def test_dynamic_progress_run_steps(monkeypatch):
    from examples import dynamic_progress as dp

    monkeypatch.setattr(dp.time, "sleep", lambda *_: None)
    task_id = dp.app_steps_progress.add_task("", total=2, name="one")
    dp.run_steps("one", (1, 1), task_id)
