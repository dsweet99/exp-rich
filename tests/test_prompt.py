import io

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt


def _ask_prompt_with_choices(*, case_sensitive: bool = True) -> tuple[str, str]:
    input_text = "egg\nFoO" if not case_sensitive else "egg\nfoo"
    console = Console(file=io.StringIO())
    name = Prompt.ask(
        "what is your name",
        console=console,
        choices=["foo", "bar"],
        default="baz",
        case_sensitive=case_sensitive,
        stream=io.StringIO(input_text),
    )
    return name, console.file.getvalue()


def test_prompt_str():
    name, output = _ask_prompt_with_choices()
    assert name == "foo"
    expected = "what is your name [foo/bar] (baz): Please select one of the available options\nwhat is your name [foo/bar] (baz): "
    print(repr(output))
    assert output == expected


def test_prompt_str_case_insensitive():
    name, output = _ask_prompt_with_choices(case_sensitive=False)
    assert name == "foo"
    expected = "what is your name [foo/bar] (baz): Please select one of the available options\nwhat is your name [foo/bar] (baz): "
    print(repr(output))
    assert output == expected


def test_prompt_str_default():
    INPUT = ""
    console = Console(file=io.StringIO())
    name = Prompt.ask(
        "what is your name",
        console=console,
        default="Will",
        stream=io.StringIO(INPUT),
    )
    assert name == "Will"
    expected = "what is your name (Will): "
    output = console.file.getvalue()
    print(repr(output))
    assert output == expected


def test_prompt_int():
    INPUT = "foo\n100"
    console = Console(file=io.StringIO())
    number = IntPrompt.ask(
        "Enter a number",
        console=console,
        stream=io.StringIO(INPUT),
    )
    assert number == 100
    expected = "Enter a number: Please enter a valid integer number\nEnter a number: "
    output = console.file.getvalue()
    print(repr(output))
    assert output == expected


def test_prompt_confirm_no():
    INPUT = "foo\nNO\nn"
    console = Console(file=io.StringIO())
    answer = Confirm.ask(
        "continue",
        console=console,
        stream=io.StringIO(INPUT),
    )
    assert answer is False
    expected = "continue [y/n]: Please enter Y or N\ncontinue [y/n]: Please enter Y or N\ncontinue [y/n]: "
    output = console.file.getvalue()
    print(repr(output))
    assert output == expected


def test_prompt_confirm_yes():
    INPUT = "foo\nNO\ny"
    console = Console(file=io.StringIO())
    answer = Confirm.ask(
        "continue",
        console=console,
        stream=io.StringIO(INPUT),
    )
    assert answer is True
    expected = "continue [y/n]: Please enter Y or N\ncontinue [y/n]: Please enter Y or N\ncontinue [y/n]: "
    output = console.file.getvalue()
    print(repr(output))
    assert output == expected


def test_prompt_confirm_default():
    INPUT = "foo\nNO\ny"
    console = Console(file=io.StringIO())
    answer = Confirm.ask(
        "continue", console=console, stream=io.StringIO(INPUT), default=True
    )
    assert answer is True
    expected = "continue [y/n] (y): Please enter Y or N\ncontinue [y/n] (y): Please enter Y or N\ncontinue [y/n] (y): "
    output = console.file.getvalue()
    print(repr(output))
    assert output == expected


def test_prompt_confirm_markup():
    INPUT = "foo\nNO\ny"
    console = Console(file=io.StringIO(), markup=False)
    answer = Confirm.ask(
        "continue", console=console, stream=io.StringIO(INPUT), default=True
    )
    assert answer is True
    expected = "continue [y/n] (y): Please enter Y or N\ncontinue [y/n] (y): Please enter Y or N\ncontinue [y/n] (y): "
    output = console.file.getvalue()
    print(repr(output))
    assert output == expected
