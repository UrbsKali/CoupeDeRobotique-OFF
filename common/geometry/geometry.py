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


class OrientedPoint(Point):
    def __init__(self, x: float, y: float, theta: float = 0.0):
        super.__init__(self, x, y)
        self.theta = theta

    @classmethod
    def from_Point(cls, point: Point, theta: float = 0):
        return cls(point.x, point.y, theta)

    def __str__(self) -> str:
        return f"Point(x={self.__point.x}, y={self.__point.y}, theta={self.theta})"

    def __repr__(self) -> str:
        return self.__str__()
