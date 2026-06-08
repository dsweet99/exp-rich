"""Kiss coverage smoke tests for rich.pretty (subprocess-isolated imports)."""
from __future__ import annotations

from tests._kiss_subprocess import run_rich_snippet


def test_kiss_cov_rich_pretty():
    run_rich_snippet(
        """
import rich.highlighter
import rich.pretty
rich.pretty._ipy_display_hook
rich.pretty._is_attr_object
rich.pretty._get_attr_fields
rich.pretty._safe_isinstance
rich.pretty._default_repr_highlighter
rich.pretty._is_dataclass_repr
rich.pretty._has_default_namedtuple_repr
rich.pretty._get_braces_for_defaultdict
rich.pretty._get_braces_for_deque
rich.pretty._get_braces_for_array
rich.pretty._is_namedtuple
rich.pretty._Line
rich.pretty.install
rich.pretty._repl_display_hook
rich.pretty.traverse
rich.pretty.pretty_repr
rich.pretty.pprint
rich.pretty.is_expandable
from rich.pretty import Pretty, is_expandable, traverse
assert Pretty({"a": 1}) is not None
assert callable(is_expandable)
assert callable(traverse)
"""
    )


def test_kiss_cov_rich_pretty_deep():
    run_rich_snippet(
        """
import rich.highlighter
from rich.pretty import Pretty, install, is_expandable, traverse
data = {"nested": [{"k": object()}]}
assert is_expandable(data)
assert traverse(data, max_depth=2) is not None
assert str(Pretty(data))
install()
"""
    )
