from shapely import (
    Point,
    MultiPoint,
    Polygon,
    MultiPolygon,
    LineString,
    BufferCapStyle,
    BufferJoinStyle,
    Geometry,
    geometry,
    prepare,
    distance,
)

from shapely.affinity import scale

from math import pi


def create_straight_rectangle(p1: Point, p2: Point) -> Polygon:
    return geometry.box(
        min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)
    )


def rad(angle: float):
    return angle * pi / 180


from typing import Any, ClassVar, Dict, Tuple

### Point inheritance: cf https://github.com/shapely/shapely/issues/1233
# Very weird but works; if not possible for some reason, maybe just migrate to a composition of Point and float instead


class OrientedPoint(Point):

    _id_to_attrs: ClassVar[Dict[str, Any]] = {}

    __slots__ = (
        Point.__slots__
    )  # slots must be the same for assigning __class__ - https://stackoverflow.com/a/52140968

    theta: float  # For documentation generation and static type checking

    def __init__(
        self, coord: Tuple[float, float], theta: float = 0.0
    ) -> (
        None
    ):  # if theta is not optional or if the structure of the arguments change (eg: self, x, y, theta) then MultiPoint becomes impossible with OrientedPoint
        self._id_to_attrs[id(self)] = dict(theta=theta)

    def __new__(cls, coord: Tuple[float, float], *args, **kwargs) -> "OrientedPoint":
        point = super().__new__(cls, coord)
        point.__class__ = cls
        return point

    def __del__(self) -> None:
        del self._id_to_attrs[id(self)]

    def __getattr__(self, name: str) -> Any:
        try:
            return OrientedPoint._id_to_attrs[id(self)][name]
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __str__(self) -> str:
        return f"{self.wkt}, theta: {self.theta}"
