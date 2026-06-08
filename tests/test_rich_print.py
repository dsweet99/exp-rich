import io
import json

import rich
from rich._console_entry import Console, console_class


def test_get_console():
    console = rich.get_console()
    assert isinstance(console, console_class())


def test_reconfigure_console():
    rich.reconfigure(width=100)
    assert rich.get_console().width == 100


def test_rich_inspect_and_extension():
    rich.inspect


def test_rich_print():
    from rich import print
    from rich import print_json

    print("kiss-cov")
    print_json(data={"a": 1})
    console = rich.get_console()
    output = io.StringIO()
    backup_file = console.file
    try:
        console.file = output
        rich.print("foo", "bar")
        rich.print("foo\n")
        rich.print("foo\n\n")
        assert output.getvalue() == "foo bar\nfoo\n\nfoo\n\n\n"
    finally:
        console.file = backup_file


def test_rich_print_json():
    console = rich.get_console()
    with console.capture() as capture:
        rich.print_json('[false, true, null, "foo"]', indent=4)
    result = capture.get()
    print(repr(result))
    expected = '[\n    false,\n    true,\n    null,\n    "foo"\n]\n'
    assert result == expected


def test_rich_print_json_round_trip():
    data = ["x" * 100, 2e128]
    console = rich.get_console()
    with console.capture() as capture:
        rich.print_json(data=data, indent=4)
    result = capture.get()
    print(repr(result))
    result_data = json.loads(result)
    assert result_data == data


def test_rich_print_json_no_truncation():
    console = rich.get_console()
    with console.capture() as capture:
        rich.print_json(f'["{"x" * 100}", {int(2e128)}]', indent=4)
    result = capture.get()
    print(repr(result))
    assert ("x" * 100) in result
    assert str(int(2e128)) in result


def test_rich_print_X():
    console = Console(file=io.StringIO(), force_terminal=True)
    output = console.file
    rich.print("foo", file=output)
    rich.print("fooX", file=output)
    rich.print("fooXX", file=output)
    assert output.getvalue() == "foo\nfooX\nfooXX\n"
