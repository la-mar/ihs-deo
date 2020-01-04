import pyproj
from pyproj import CRS, Transformer


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
        if all([x is not None, y is not None, crs is not None]):
            src = CRS.from_epsg(self.lookup_epsg(crs))
            dest = CRS.from_epsg(self.lookup_epsg(self.crs))
            transformer = Transformer.from_crs(src, dest, always_xy=True)
            return (*transformer.transform(x, y), self.crs)

        else:
            return x, y, crs


if __name__ == "__main__":

    ct = CoordinateTransformer("wgs84")
    lon, lat = [-101.9179619, 31.2029678]
    crs = "NAD27"
    result = ct.transform(lon, lat, crs)
    result = (round(result[0], 7), round(result[1], 7), "wgs84")
    expected = (-101.9183695, 31.2031166, "wgs84")

    print("nad27s -> wgs84")
    print(result)
    print(result == expected)

    x, y = [1504599.4, 562258.6]
    crs = "NAD27SP"
    ct.transform(x, y, crs)

    print("nad27sp -> wgs84")
    print(result)
    print(result == expected)
