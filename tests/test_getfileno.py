from types import SimpleNamespace

from rich._fileno import get_fileno


def test_get_fileno():
    file_like = SimpleNamespace(fileno=lambda: 123)
    assert get_fileno(file_like) == 123


def test_get_fileno_missing():
    file_like = SimpleNamespace()
    assert get_fileno(file_like) is None


def test_get_fileno_broken():
    def broken_fileno() -> int:
        1 / 0
        return 123

    file_like = SimpleNamespace(fileno=broken_fileno)
    assert get_fileno(file_like) is None
