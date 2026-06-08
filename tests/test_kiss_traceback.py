import io

from rich.console import Console
from rich.traceback import Frame, Trace, Traceback, install as traceback_install


def test_traceback_kiss_symbols():
    traceback_install(console=Console(file=io.StringIO()))
    assert Frame is not None
    assert Trace is not None
    assert Traceback is not None
    assert Traceback.extract is not None
    assert traceback_install is not None
