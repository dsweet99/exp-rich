"""Kiss static references for rich._pretty_bridge."""

from rich._pretty_bridge import pretty_helpers, register_pretty_module


def test_register_pretty_module_and_helpers():
    import rich.pretty as pretty_mod

    register_pretty_module(pretty_mod)
    Pretty, is_expandable = pretty_helpers()
    assert Pretty is pretty_mod.Pretty
    assert callable(is_expandable)
