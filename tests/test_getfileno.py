def test_get_fileno():
    from rich._console_write import get_fileno

    FileLike = type("FileLike", (), {"fileno": lambda self: 123})
    assert get_fileno(FileLike()) == 123


def test_get_fileno_missing():
    from rich._console_write import get_fileno

    FileLike = type("FileLike", (), {})
    assert get_fileno(FileLike()) is None


def test_get_fileno_broken():
    from rich._console_write import get_fileno

    def fileno(self) -> int:
        1 / 0
        return 123

    FileLike = type("FileLike", (), {"fileno": fileno})
    assert get_fileno(FileLike()) is None
