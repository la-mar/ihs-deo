import pyproj
import functools

EPSG_MAP = {
    "nad27:texas central": 32039,
    "nad27sp": 32039,
    "nad27": 4267,
    "wgs84": 4326,
}


class CoordinateTransformer:
    """ Normalizes arbirary coordinates from their native datum/CRS to the destination
        coordination reference system """

    crs = "wgs84"

    def __init__(self, crs: str = None):
        self.crs = crs or self.crs

    def __repr__(self):
        return f"CoordinateTransformer: {self.crs}"

    def lookup_epsg(self, name: str):
        return EPSG_MAP.get(str(name).lower())

    def transform(self, x: float, y: float, crs: str):

        source_proj = pyproj.Proj(init=f"epsg:{self.lookup_epsg(crs)}")
        dest_proj = pyproj.Proj(init=f"epsg:{self.lookup_epsg(self.crs)}")
        return (*pyproj.transform(source_proj, dest_proj, x, y), self.crs)


if __name__ == "__main__":
    ct = CoordinateTransformer("wgs84")

    lon, lat = [-101.9179619, 31.2029678]
    crs = "NAD27"
    ct.transform(lon, lat, crs)

    x, y = [1504599.4, 562258.6]
    crs = "NAD27SP"
    ct.transform(x, y, crs)
