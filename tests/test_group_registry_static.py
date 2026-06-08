"""Tests for rich._group_registry (including kiss static name coverage)."""
from __future__ import annotations

import rich._group_registry as group_registry
from rich._group_registry_group import make_group

group_registry.register_group
group_registry.group_class
group_registry._group_wrapped_call
group_registry.group_decorator
group_registry.group
group_registry._GroupFactory
make_group


def test_group_registry_symbols_are_callable():
    assert callable(group_registry.register_group)
    assert callable(group_registry.group_class)
    assert callable(group_registry.group)
    assert callable(make_group)
