"""Tests for rich._group_registry."""
from __future__ import annotations

import rich._group_registry as group_registry
from rich._console_types import Group
from rich._group_registry import Group as GroupFactory, group, group_class, register_group

group_registry.register_group
group_registry.group_class
group_registry._GroupFactory
group_registry.group_decorator
group_registry._group_wrapped_call


def test_group_registry_register_and_decorator():
    register_group(Group)

    @group(fit=True)
    def make_items():
        return ["a", "b"]

    grouped = make_items()
    assert isinstance(grouped, Group)
    assert grouped.fit is True
    assert group_class() is Group


def test_group_factory_callable():
    register_group(Group)
    grouped = GroupFactory("x", "y", fit=False)
    assert grouped.fit is False
