import numpy as np
import pandas as pd

from model.ocean_devices.Seabed import Seabed
from model.Table import Table
from model.Spikes import Spikes


class PandasSeabedAnalyzer:

    def __init__(self, *seabeds: Seabed):
        self.all_salinity = []
        if seabeds is not ():
            for seabed in seabeds:
                self.all_salinity.extend(seabed.salinity_psu)
            self.spike_threshold = self.__calculate_spike_threshold(self.all_salinity)

    def describe(self, seabed: Seabed) -> Table:
        described = self.__create_df(seabed).describe()
        described.loc["mean", "TimeStamp"] = None
        return self.__create_table_from_df(described)

    def analyze_null_and_unique_values(self, seabed: Seabed) -> Table:
        df = self.__create_df(seabed)
        return self.__create_table_from_df(pd.DataFrame({
            "Null_values": df.isna().sum(),
            "Unique values": df.nunique()
        }))

    def data_continuity(self, seabed: Seabed, count_threshold: int) -> Table:
        df = self.__create_df(seabed)
        diff = self.__calculate_time_anomalies(df, count_threshold)
        return self.__create_table_from_df(pd.DataFrame(
            {"Difference": diff["TimeStamp"].reset_index(drop=True),
             "Previous TimeStamp": df.loc[diff.index - 1, "TimeStamp"].reset_index(drop=True),
             "Next TimeStamp": df.loc[diff.index, "TimeStamp"].reset_index(drop=True)}))

    def __calculate_time_anomalies(self, df: pd.DataFrame, count_threshold: int) -> pd.DataFrame:
        diff = df.diff(periods=1)
        value_counts = diff["TimeStamp"].value_counts().reset_index()
        return diff[diff["TimeStamp"].isin(value_counts[value_counts["count"] < count_threshold]["TimeStamp"])]

    def analyze_outliers_salinity(self, seabed: Seabed) -> Spikes:
        return self.__spike_test(self.__create_df(seabed), Spikes.SpikeVariable.SALINITY_PSU)

    def __spike_test(self, df: pd.DataFrame, variable_name: Spikes.SpikeVariable) -> Spikes:
        spike_threshold = self.spike_threshold
        df.loc[0, 'test value'] = None
        for i in range(1, len(df) - 1):
            self.__calculate_test_value_from_df_index(df, i, variable_name.value)
        outliers = self.__filter_values_by_spike_test(df, spike_threshold)
        return Spikes([variable_name] * len(outliers.index), spike_threshold, list(outliers["TimeStamp"].dt.to_pydatetime()),
                      list(outliers[variable_name.value]), list(outliers.index))

    def __filter_values_by_spike_test(self, df, spike_threshold):
        return df[df['test value'] > spike_threshold]

    def __calculate_test_value_from_df_index(self, df: pd.DataFrame, i: int, variable_name: str):
        V1 = df.loc[i - 1, variable_name]
        V2 = df.loc[i, variable_name]
        V3 = df.loc[i + 1, variable_name]
        df.loc[i, 'test value'] = abs(V2 - (V3 + V1) / 2) - abs((V3 - V1) / 2)

    def __calculate_spike_threshold(self, variable: list[float]) -> float:
        q75, q25 = np.percentile(variable, [75, 25])
        iqr = q75 - q25
        spike_threshold = iqr * 1.5
        return spike_threshold

    def __create_df(self, seabed: Seabed) -> pd.DataFrame:
        return pd.DataFrame({
            "TimeStamp": seabed.timestamp,
            "Temperature_C": seabed.temperature_c,
            "Conductivity_S_m": seabed.conductivity_s_m,
            "Salinity_PSU": seabed.salinity_psu
        })

    def __create_table_from_df(self, described: pd.DataFrame) -> Table:
        return Table(list(map(lambda label: Table.Column(label, list(described[label])), list(described.columns))), list(described.index))
