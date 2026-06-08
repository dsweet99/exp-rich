from typing import List

try:
    import attr
except ImportError:
    print("This example requires attrs library")
    print("pip install attrs")
    raise SystemExit()

from examples.attrs_point3d import Point3D
from examples.attrs_triangle import Triangle


@attr.define
class Model:
    name: str
    triangles: List[Triangle] = attr.Factory(list)


if __name__ == "__main__":
    model = Model(
        name="Alien#1",
        triangles=[
            Triangle(
                Point3D(x=20, y=50),
                Point3D(x=50, y=15, z=-45.34),
                Point3D(3.1426, 83.2323, -16),
            )
        ],
    )

    from rich._console_entry import Console
    from rich.pretty import Pretty
    from rich.table import Column, Table
    from rich.text import Text

    console = Console()

    table = Table("attrs *with* Rich", Column(Text.from_markup("attrs *without* Rich")))

    table.add_row(Pretty(model), repr(model))
    console.print(table)
