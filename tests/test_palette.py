from rich._palettes import STANDARD_PALETTE
from rich.color_triplet import ColorTriplet
from rich.palette import Palette
from rich.table import Table


def test_rich_cast():
    table = STANDARD_PALETTE.__rich__()
    assert isinstance(table, Table)
    assert table.row_count == 16


def test_palette_index_and_match() -> None:
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    palette = Palette(colors)

    assert palette[0] == ColorTriplet(255, 0, 0)
    assert palette.match((250, 5, 5)) == 0
    assert palette.match((5, 250, 5)) == 1
    assert palette.match((5, 5, 250)) == 2


def test_palette_rich() -> None:
    palette = Palette([(255, 0, 0), (0, 255, 0)])
    table = palette.__rich__()
    assert isinstance(table, Table)
    assert table.row_count == 2
