from rich.palette import STANDARD_PALETTE


def test_palette_match():
    assert STANDARD_PALETTE.match((200, 0, 0)) == 1
