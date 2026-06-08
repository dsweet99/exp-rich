import rich.highlighter  # noqa: F401  # registers JSON highlight kernel
import rich.text  # noqa: F401
from rich.json import JSON
import datetime


def test_print_json_data_with_default():
    date = datetime.date(2021, 1, 1)
    json = JSON.from_data({"date": date}, default=lambda d: d.isoformat())
    assert str(json.text) == '{\n  "date": "2021-01-01"\n}'


def test_json_highlight_kernel_registered():
    from rich._json_highlight import highlight_json

    highlighted = highlight_json('{"key": "value"}', highlight=True)
    assert "key" in str(highlighted)

    plain = highlight_json('{"key": "value"}', highlight=False)
    assert plain.plain == '{"key": "value"}'


def test_json_highlight_kernel_register():
    from rich._json_highlight import highlight_json, register_json_highlight
    from rich.highlighter import JSONHighlighter
    from rich.text import Text

    register_json_highlight(lambda s: Text(f"hl:{s}"), Text)
    assert highlight_json("{}", highlight=True).plain == "hl:{}"
    assert highlight_json("{}", highlight=False).plain == "{}"
    register_json_highlight(JSONHighlighter().__call__, Text)


def test_json_highlight_keys_helper():
    from rich._json_highlight import highlight_json_keys
    from rich._highlight_kernel import span_class
    from rich.text import Text

    json_str = r'(?P<str>"[^"]*")'
    text = Text('"key" : "value"')
    highlight_json_keys(text, json_str, frozenset({" "}), span_class())
    text2 = Text('"key"x"value"')
    highlight_json_keys(text2, json_str, frozenset({" "}), span_class())
    assert text.plain == '"key" : "value"'
