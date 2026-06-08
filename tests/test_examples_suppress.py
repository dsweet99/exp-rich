"""Example test: suppress demo."""

from __future__ import annotations

import pytest


def test_suppress_hello():
    pytest.importorskip("click")
    from click.testing import CliRunner
    from examples.suppress import hello

    runner = CliRunner()
    result = runner.invoke(hello, ["--count", "1"])
    assert result.exit_code != 0
    assert hello is not None
