"""Tests for examples.top_lite_simulator."""
from __future__ import annotations

import datetime


def test_process_table_and_formatting():
    from examples import top_lite_simulator as sim

    proc = sim.generate_process(1)
    assert proc.pid == 1
    assert proc.memory_str
    assert proc.time_str
    sim.create_process_table(5)

    direct = sim.Process(
        pid=99,
        command="test",
        cpu_percent=1.0,
        memory=500,
        start_time=datetime.datetime.now(),
        thread_count=1,
        state="running",
    )
    assert direct.memory_str == "500"
    assert direct.time_str
