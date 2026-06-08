# encoding=utf-8

import io

from rich.columns import Columns
from rich.console import Console

COLUMN_DATA = [
    "Ursus americanus",
    "American buffalo",
    "Bison bison",
    "American crow",
    "Corvus brachyrhynchos",
    "American marten",
    "Martes americana",
    "American racer",
    "Coluber constrictor",
    "American woodcock",
    "Scolopax minor",
    "Anaconda (unidentified)",
    "Eunectes sp.",
    "Andean goose",
    "Chloephaga melanoptera",
    "Ant",
    "Anteater, australian spiny",
    "Tachyglossus aculeatus",
    "Anteater, giant",
]


def _print_columns_layout(
    console: Console, columns: Columns, rule: str, **attributes: object
) -> None:
    for name, value in attributes.items():
        setattr(columns, name, value)
    console.rule(rule)
    console.print(columns)


def render():
    console = Console(file=io.StringIO(), width=100, legacy_windows=False)

    console.rule("empty")
    empty_columns = Columns([])
    console.print(empty_columns)
    columns = Columns(COLUMN_DATA)
    columns.add_renderable("Myrmecophaga tridactyla")
    _print_columns_layout(console, columns, "optimal")
    _print_columns_layout(console, columns, "optimal, expand", expand=True)
    _print_columns_layout(
        console, columns, "column first, optimal", column_first=True, expand=False
    )
    _print_columns_layout(
        console, columns, "column first, right to left", right_to_left=True
    )
    _print_columns_layout(
        console, columns, "equal columns, expand", equal=True, expand=True
    )
    _print_columns_layout(
        console, columns, "fixed width", width=16, expand=False
    )
    console.print()
    render_result = console.file.getvalue()
    print(render_result)
    print(repr(render_result))
    return render_result


def test_render():
    expected = "────────────────────────────────────────────── empty ───────────────────────────────────────────────\n───────────────────────────────────────────── optimal ──────────────────────────────────────────────\nUrsus americanus           American buffalo       Bison bison            American crow          \nCorvus brachyrhynchos      American marten        Martes americana       American racer         \nColuber constrictor        American woodcock      Scolopax minor         Anaconda (unidentified)\nEunectes sp.               Andean goose           Chloephaga melanoptera Ant                    \nAnteater, australian spiny Tachyglossus aculeatus Anteater, giant        Myrmecophaga tridactyla\n───────────────────────────────────────── optimal, expand ──────────────────────────────────────────\nUrsus americanus             American buffalo        Bison bison             American crow          \nCorvus brachyrhynchos        American marten         Martes americana        American racer         \nColuber constrictor          American woodcock       Scolopax minor          Anaconda (unidentified)\nEunectes sp.                 Andean goose            Chloephaga melanoptera  Ant                    \nAnteater, australian spiny   Tachyglossus aculeatus  Anteater, giant         Myrmecophaga tridactyla\n────────────────────────────────────── column first, optimal ───────────────────────────────────────\nUrsus americanus      American marten     Scolopax minor          Ant                       \nAmerican buffalo      Martes americana    Anaconda (unidentified) Anteater, australian spiny\nBison bison           American racer      Eunectes sp.            Tachyglossus aculeatus    \nAmerican crow         Coluber constrictor Andean goose            Anteater, giant           \nCorvus brachyrhynchos American woodcock   Chloephaga melanoptera  Myrmecophaga tridactyla   \n─────────────────────────────────── column first, right to left ────────────────────────────────────\nAnt                        Scolopax minor          American marten     Ursus americanus     \nAnteater, australian spiny Anaconda (unidentified) Martes americana    American buffalo     \nTachyglossus aculeatus     Eunectes sp.            American racer      Bison bison          \nAnteater, giant            Andean goose            Coluber constrictor American crow        \nMyrmecophaga tridactyla    Chloephaga melanoptera  American woodcock   Corvus brachyrhynchos\n────────────────────────────────────── equal columns, expand ───────────────────────────────────────\nChloephaga melanoptera                American racer                    Ursus americanus            \nAnt                                   Coluber constrictor               American buffalo            \nAnteater, australian spiny            American woodcock                 Bison bison                 \nTachyglossus aculeatus                Scolopax minor                    American crow               \nAnteater, giant                       Anaconda (unidentified)           Corvus brachyrhynchos       \nMyrmecophaga tridactyla               Eunectes sp.                      American marten             \n                                      Andean goose                      Martes americana            \n─────────────────────────────────────────── fixed width ────────────────────────────────────────────\nAnteater,        Eunectes sp.     Coluber          Corvus           Ursus americanus\naustralian spiny                  constrictor      brachyrhynchos                   \nTachyglossus     Andean goose     American         American marten  American buffalo\naculeatus                         woodcock                                          \nAnteater, giant  Chloephaga       Scolopax minor   Martes americana Bison bison     \n                 melanoptera                                                        \nMyrmecophaga     Ant              Anaconda         American racer   American crow   \ntridactyla                        (unidentified)                                    \n\n"
    print("--")
    print(expected)
    print("--")
    assert render() == expected


if __name__ == "__main__":
    result = render()
    print(result)
    print(repr(result))
