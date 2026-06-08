try:
    import attr
except ImportError:
    raise SystemExit()


@attr.define
class Point3D:
    x: float
    y: float
    z: float = 0
