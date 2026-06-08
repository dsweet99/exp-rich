"""Tests for rich._pretty_install helpers."""
from __future__ import annotations

from rich._pretty_install import build_install, run_install

run_install
build_install


def test_run_install_repl_branch():
    calls: list[str] = []

    def fake_get_ipython() -> None:
        raise NameError

    run_install(
        None,
        "ignore",
        False,
        False,
        None,
        None,
        None,
        False,
        lambda: object(),
        fake_get_ipython,
        lambda *args, **kwargs: calls.append("repl"),
        lambda *args, **kwargs: calls.append("ipython"),
    )
    assert calls == ["repl"]


def test_build_install_returns_callable():
    install_fn = build_install(lambda: object(), lambda **_: None, lambda **_: None)
    assert callable(install_fn)
