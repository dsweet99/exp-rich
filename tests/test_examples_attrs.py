"""Example tests: attrs demo (subprocess isolation for kiss)."""
from __future__ import annotations

import subprocess
import sys
import textwrap


def test_attrs_example():
    script = textwrap.dedent(
        """
        from examples.attrs import Model, Point3D, Triangle

        model = Model(
            name="Alien#1",
            triangles=[
                Triangle(Point3D(1, 2), Point3D(3, 4, 5), Point3D(6, 7, 8)),
            ],
        )
        assert model.name == "Alien#1"
        """
    )
    subprocess.run([sys.executable, "-c", script], check=True)
