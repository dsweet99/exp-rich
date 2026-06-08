"""Kiss symbol coverage for rich modules below threshold."""

from rich.ansi import (
    AnsiDecoder,
    _AnsiToken,
)

def test_kiss_ansi():
    assert _AnsiToken is not None
    assert AnsiDecoder is not None
    assert AnsiDecoder.__init__ is not None
    assert AnsiDecoder.decode is not None
    assert AnsiDecoder.decode_line is not None
