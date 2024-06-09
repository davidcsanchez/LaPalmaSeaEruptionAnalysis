import geopandas as gpd


class GeoJsonGeoPandasExtractor:
    def extract(self, geojson: str) -> gpd.GeoDataFrame:
        return gpd.read_file(geojson)
