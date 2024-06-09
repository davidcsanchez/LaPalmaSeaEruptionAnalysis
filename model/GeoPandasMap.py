import pandas as pd
from matplotlib.colors import ListedColormap


class GeoPandasMap:
    def __init__(self, geopandas_df: pd.DataFrame):
        self.data = geopandas_df

    def plot(self, ax, column: str, legend: True, cmap: ListedColormap, legend_kwds: dict):
        self.data.plot(ax=ax, column=column, legend=legend, cmap=cmap, legend_kwds=legend_kwds)

    def __eq__(self, other):
        return self.data == other.data
