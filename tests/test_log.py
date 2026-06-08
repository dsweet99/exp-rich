# encoding=utf-8


import io

from rich._console_entry import Console, console_class

from .render import replace_link_ids


test_data = [1, 2, 3]


def render_log():
    console = Console(
        file=io.StringIO(),
        width=80,
        force_terminal=True,
        log_time_format="[TIME]",
        color_system="truecolor",
        legacy_windows=False,
    )
    console.log()
    console.log("Hello from", console, "!")
    console.log(test_data, log_locals=True)
    return replace_link_ids(console.file.getvalue()).replace("test_log.py", "source.py")


def test_log():
    expected = replace_link_ids(
        "\x1b[2;36m[TIME]\x1b[0m\x1b[2;36m \x1b[0m                                                           \x1b]8;id=0;foo\x1b\\\x1b[2msource.py\x1b[0m\x1b]8;;\x1b\\\x1b[2m:\x1b[0m\x1b]8;id=0;foo\x1b\\\x1b[2m23\x1b[0m\x1b]8;;\x1b\\\n\x1b[2;36m      \x1b[0m\x1b[2;36m \x1b[0mHello from \x1b[1m<\x1b[0m\x1b[1;95mconsole\x1b[0m\x1b[39m \x1b[0m\x1b[33mwidth\x1b[0m\x1b[39m=\x1b[0m\x1b[1;36m80\x1b[0m\x1b[39m ColorSystem.TRUECOLOR\x1b[0m\x1b[1m>\x1b[0m !      \x1b]8;id=0;foo\x1b\\\x1b[2msource.py\x1b[0m\x1b]8;;\x1b\\\x1b[2m:\x1b[0m\x1b]8;id=0;foo\x1b\\\x1b[2m24\x1b[0m\x1b]8;;\x1b\\\n\x1b[2;36m      \x1b[0m\x1b[2;36m \x1b[0m\x1b[1m[\x1b[0m\x1b[1;36m1\x1b[0m, \x1b[1;36m2\x1b[0m, \x1b[1;36m3\x1b[0m\x1b[1m]\x1b[0m                                                  \x1b]8;id=0;foo\x1b\\\x1b[2msource.py\x1b[0m\x1b]8;;\x1b\\\x1b[2m:\x1b[0m\x1b]8;id=0;foo\x1b\\\x1b[2m25\x1b[0m\x1b]8;;\x1b\\\n\x1b[2;36m       \x1b[0m\x1b[34m╭─\x1b[0m\x1b[34m─────────────────────\x1b[0m\x1b[34m \x1b[0m\x1b[3;34mlocals\x1b[0m\x1b[34m \x1b[0m\x1b[34m─────────────────────\x1b[0m\x1b[34m─╮\x1b[0m     \x1b[2m              \x1b[0m\n\x1b[2;36m       \x1b[0m\x1b[34m│\x1b[0m \x1b[3;33mconsole\x1b[0m\x1b[31m =\x1b[0m \x1b[1m<\x1b[0m\x1b[1;95mconsole\x1b[0m\x1b[39m \x1b[0m\x1b[33mwidth\x1b[0m\x1b[39m=\x1b[0m\x1b[1;36m80\x1b[0m\x1b[39m ColorSystem.TRUECOLOR\x1b[0m\x1b[1m>\x1b[0m \x1b[34m│\x1b[0m     \x1b[2m              \x1b[0m\n\x1b[2;36m       \x1b[0m\x1b[34m╰────────────────────────────────────────────────────╯\x1b[0m     \x1b[2m              \x1b[0m\n"
    )
    rendered = render_log()
    print(repr(rendered))
    assert rendered == expected


def test_log_caller_frame_info():
    ConsoleClass = console_class()
    for i in range(2):
        assert ConsoleClass._caller_frame_info(i) == ConsoleClass._caller_frame_info(
            i, lambda: None
        )


def test_justify():
    console = Console(width=20, log_path=False, log_time=False, color_system=None)
    console.begin_capture()
    console.log("foo", justify="right")
    result = console.end_capture()
    assert result == "                 foo\n"


if __name__ == "__main__":
    render = render_log()
    print(render)
    print(repr(render))
