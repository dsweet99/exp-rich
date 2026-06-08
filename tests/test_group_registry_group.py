"""Dedicated kiss coverage for rich._group_registry.group (import + call)."""
from __future__ import annotations

from rich._console_types import Group
from rich._group_registry import group, register_group


def test_group_registry_group_import_and_call():
    register_group(Group)

    @group(fit=True)
    def make_renderables():
        return ["x"]

    result = make_renderables()
    assert isinstance(result, Group)
    assert result.fit is True


def test_group_default_fit_parameter():
    register_group(Group)
    decorator = group()
    assert callable(decorator)

    @decorator
    def make_renderables():
        return ["a", "b"]

    grouped = make_renderables()
    assert isinstance(grouped, Group)
    assert grouped.fit is True
    assert list(grouped.renderables) == ["a", "b"]
