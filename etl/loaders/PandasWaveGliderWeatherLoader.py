from datetime import datetime

import pandas as pd
from pandas.core.dtypes.common import is_datetime64_any_dtype

from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather


class PandasWaveGliderWeatherLoader:
    def load(self, df: pd.DataFrame) -> WaveGliderV2Weather:
        return WaveGliderV2Weather(
            self.date_column_to_list(df["TimeStamp"]),
            df["Temperature_C"].to_list(),
            df["Wind_speed_kt"].to_list(),
            df["Wind_gust_speed_kt"].to_list(),
            df["Wind_direction"].to_list(),
            df["Latitude_deg"].to_list(),
            df["Longitude_deg"].to_list()
        )

    def date_column_to_list(self, column: pd.Series) -> list[datetime]:
        if is_datetime64_any_dtype(column):
            return list(column.dt.to_pydatetime())
        return column.to_list()
