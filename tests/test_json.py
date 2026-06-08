from rich._json_format import encode_json_text, highlight_json_text
from rich.json import JSON
from rich.text import Text
import datetime


def test_print_json_data_with_default():
    date = datetime.date(2021, 1, 1)
    json = JSON.from_data({"date": date}, default=lambda d: d.isoformat())
    assert str(json.text) == '{\n  "date": "2021-01-01"\n}'


def test_highlight_json_text_marks_keys_and_literals():
    text = Text('{"name": "alice", "count": 1, true, false, null}')
    highlighted = highlight_json_text(text)
    styles = {span.style for span in highlighted.spans if span.style}
    assert "json.key" in styles
    assert any(style and style.startswith("json.") for style in styles)


def test_encode_json_text_round_trip():
    encoded = encode_json_text({"items": [1, 2], "ok": True}, indent=2)
    assert '"items"' in encoded.plain
    assert '"ok"' in encoded.plain
    assert encoded.no_wrap is True
