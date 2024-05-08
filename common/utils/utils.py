from datetime import datetime, timedelta
from shapely import Geometry, Point


class Utils:
    @staticmethod
    def get_date() -> datetime:
        return datetime.now()

    @staticmethod
    def get_str_date(format: str = "%H:%M:%S") -> str:
        return datetime.now().strftime(format)

    @staticmethod
    def get_ts() -> float:
        return datetime.timestamp(datetime.now())

    @staticmethod
    def time_since(ts: float) -> float:
        return Utils.get_ts() - ts

    @staticmethod
    def geom_to_str(geom: Geometry):
        r = ""
        if isinstance(geom, Point):
            r = str((round(geom.x), round(geom.y)))

        else:
            try:
                r = (
                    "["
                    + ", ".join(
                        [Utils.geom_to_str(smaller_geom) for smaller_geom in geom.geoms]
                    )
                    + "]"
                )
            except:
                r = str(geom)

        return r
