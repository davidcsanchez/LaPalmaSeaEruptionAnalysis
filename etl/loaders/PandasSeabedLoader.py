from datetime import datetime

import pandas as pd
from pandas.core.dtypes.common import is_datetime64_any_dtype

from model.ocean_devices.Seabed import Seabed


class PandasSeabedLoader:

    def load(self, df: pd.DataFrame) -> Seabed:
        return Seabed(self.date_column_to_list(df["TimeStamp"]),
                      df["Temperature_C"].to_list(),
                      df["Conductivity_S_m"].to_list(),
                      df["Salinity_PSU"].to_list()
                      )

    def date_column_to_list(self, column: pd.Series) -> list[datetime]:
        if is_datetime64_any_dtype(column):
            return list(column.dt.to_pydatetime())
        return column.to_list()
