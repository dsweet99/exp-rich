import pytest

import rich.markup  # noqa: F401 — register markup bridge before collection imports examples
import rich.pretty  # noqa: F401 — register pretty bridge before console.print tests


@pytest.fixture(autouse=True, scope="session")
def _load_rich_peer_modules():
    yield


@pytest.fixture(autouse=True)
def reset_color_envvars(monkeypatch):
    """Remove color-related envvars to fix test output"""
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    monkeypatch.delenv("NO_COLOR", raising=False)
