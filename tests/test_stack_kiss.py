"""Kiss static references for rich._stack."""

from rich._stack import RichStackList


def test_rich_stack_class():
    stack = RichStackList()
    stack.push("x")
    assert stack.top == "x"
