"""Kiss static references for rich.ansi PTY helper."""

import io
from unittest.mock import patch

from rich.ansi import AnsiDecoder, ansi_example_read


def test_ansi_example_read():
    buffer = io.BytesIO()
    with patch("os.read", return_value=b"x"):
        data = ansi_example_read(0, buffer)
    assert data == b"x"
    assert buffer.getvalue() == b"x"
    assert AnsiDecoder is not None
