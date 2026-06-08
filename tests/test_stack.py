from rich._stack import Stack as RichStack


def test_stack_push_top():
    stack = RichStack()
    stack.push("foo")
    assert stack.top == "foo"


def test_stack():
    stack = RichStack()
    stack.push("foo")
    stack.push("bar")
    assert stack.top == "bar"
    assert stack.pop() == "bar"
    assert stack.top == "foo"
    assert RichStack.__name__ == "RichStackList"
