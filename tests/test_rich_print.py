import io
import json

import rich
from rich import print, print_json
from rich.console import Console


def test_rich_init_print_functions():
    console = Console(file=io.StringIO(), width=80)
    original = rich.get_console
    rich.get_console = lambda: console
    try:
        print("direct")
        print_json(data={"k": 1})
    finally:
        rich.get_console = original
    assert "direct" in console.file.getvalue()


def test_get_console():
    console = rich.get_console()
    assert isinstance(console, Console)


def test_reconfigure_console():
    rich.reconfigure(width=100)
    assert rich.get_console().width == 100


def test_rich_print():
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
    console = rich.get_console()
    output = io.StringIO()
    backup_file = console.file
    try:
        console.file = output
        rich.print("foo")
        rich.print("fooX")
        rich.print("fooXX")
        assert output.getvalue() == "foo\nfooX\nfooXX\n"
    finally:
        console.file = backup_file
