try:
    import attr
except ImportError:
    raise SystemExit()

from examples.attrs_point3d import Point3D


@attr.define
class Triangle:
    point1: Point3D
    point2: Point3D
    point3: Point3D
