import io


def _ask_prompt_with_retry(
    input_text: str, *, case_sensitive: bool = True
) -> tuple[str, str]:
    from rich._console_entry import Console
    from rich.prompt import Prompt

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
    name, output = _ask_prompt_with_retry("egg\nfoo")
    assert name == "foo"
    print(repr(output))
    assert output == (
        "what is your name [foo/bar] (baz): Please select one of the available options\n"
        "what is your name [foo/bar] (baz): "
    )


def test_prompt_str_case_insensitive():
    name, output = _ask_prompt_with_retry("egg\nFoO", case_sensitive=False)
    assert name == "foo"
    print(repr(output))
    assert output == (
        "what is your name [foo/bar] (baz): Please select one of the available options\n"
        "what is your name [foo/bar] (baz): "
    )


def test_prompt_str_default():
    from rich._console_entry import Console
    from rich.prompt import Prompt

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
    from rich._console_entry import Console
    from rich.prompt import IntPrompt

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
    from rich._console_entry import Console
    from rich.prompt import Confirm

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
    from rich._console_entry import Console
    from rich.prompt import Confirm

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
    from rich._console_entry import Console
    from rich.prompt import Confirm

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
    from rich._console_entry import Console
    from rich.prompt import Confirm

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
