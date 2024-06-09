import pandas as pd

from model.GeoPandasMap import GeoPandasMap


class GeoPandasMapLoader:

    def load(self, geopandas_df: pd.DataFrame) -> GeoPandasMap:
        return GeoPandasMap(geopandas_df)
