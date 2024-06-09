import numpy as np
import pandas as pd

from model.Spikes import Spikes
from model.Table import Table
from model.ocean_devices.WaveGliderV2Ocean import WaveGliderV2Ocean


class PandasWaveGliderV2OceanAnalyzer:

    def __init__(self, *wave_gliders: WaveGliderV2Ocean):
        self.all_salinity = []
        self.all_oxygen = []
        if wave_gliders is not ():
            for wave_glider in wave_gliders:
                self.all_salinity.extend(wave_glider.salinity_psu)
                self.all_oxygen.extend(wave_glider.oxygen)
            self.spike_threshold_sal = self.__calculate_spike_threshold(self.all_salinity)
            self.spike_threshold_ox = self.__calculate_spike_threshold(self.all_oxygen)

    def describe(self, glider: WaveGliderV2Ocean) -> Table:
        described = self.__create_df(glider).describe()
        described.loc["mean", "TimeStamp"] = None
        return self.__create_table_from_df(described)

    def analyze_null_and_unique_values(self, glider: WaveGliderV2Ocean) -> Table:
        df = self.__create_df(glider)
        return self.__create_table_from_df(pd.DataFrame({
            "Null_values": df.isna().sum(),
            "Unique values": df.nunique()
        }))

    def data_continuity(self, glider: WaveGliderV2Ocean, count_threshold: int) -> Table:
        df = self.__create_df(glider)
        diff = self.__calculate_time_anomalies(df, count_threshold)
        return self.__create_table_from_df(pd.DataFrame(
            {"Difference": diff["TimeStamp"].reset_index(drop=True),
             "Previous TimeStamp": df.loc[diff.index - 1, "TimeStamp"].reset_index(drop=True),
             "Next TimeStamp": df.loc[diff.index, "TimeStamp"].reset_index(drop=True)}))

    def analyze_outliers_salinity(self, wave_glider: WaveGliderV2Ocean) -> Spikes:
        return self.__spike_test(self.__create_df(wave_glider),
                                 Spikes.SpikeVariable.SALINITY_PSU,self.spike_threshold_sal)

    def analyze_outliers_oxygen(self, wave_glider: WaveGliderV2Ocean) -> Spikes:
        return self.__spike_test(self.__create_df(wave_glider),
                                 Spikes.SpikeVariable.OXYGEN_UMOL_L, self.spike_threshold_ox)

    def __spike_test(self, df: pd.DataFrame,  variable_enum: Spikes.SpikeVariable, spike_threshold: float) -> Spikes:
        df.loc[0, 'test value'] = None
        for i in range(1, len(df) - 1):
            self.__calculate_test_value_from_df_index(df, i, variable_enum.value)
        outliers = self.__filter_values_by_spike_test(df, spike_threshold)
        return Spikes([variable_enum] * len(outliers.index), spike_threshold, list(outliers["TimeStamp"].dt.to_pydatetime()),
                      list(outliers[variable_enum.value]), list(outliers.index))

    def __filter_values_by_spike_test(self, df: pd.DataFrame, spike_threshold: float) -> pd.DataFrame:
        return df[df['test value'] > spike_threshold]

    def __calculate_test_value_from_df_index(self, df: pd.DataFrame, i: int, variable_name: str) -> None:
        V1 = df.loc[i - 1, variable_name]
        V2 = df.loc[i, variable_name]
        V3 = df.loc[i + 1, variable_name]
        df.loc[i, 'test value'] = abs(V2 - (V3 + V1) / 2) - abs((V3 - V1) / 2)

    def __calculate_spike_threshold(self, variable: list[float]) -> float:
        q75, q25 = np.percentile(variable, [75, 25])
        iqr = q75 - q25
        spike_threshold = iqr * 1.5
        return spike_threshold

    def __calculate_time_anomalies(self, df: pd.DataFrame, count_threshold: int) -> pd.DataFrame:
        diff = df.diff(periods=1)
        value_counts = diff["TimeStamp"].value_counts().reset_index()
        return diff[diff["TimeStamp"].isin(value_counts[value_counts["count"] < count_threshold]["TimeStamp"])]

    def __create_df(self, glider: WaveGliderV2Ocean) -> pd.DataFrame:
        return pd.DataFrame({
            "TimeStamp": glider.timestamp,
            "Temperature_C": glider.temperature_c,
            "Conductivity_S_m": glider.conductivity_s_m,
            "Salinity_PSU": glider.salinity_psu,
            "Pressure_d": glider.pressure_d,
            "Oxygen_umol_L": glider.oxygen
        })

    def __create_table_from_df(self, df: pd.DataFrame) -> Table:
        return Table(list(map(lambda label: Table.Column(label, list(df[label])), list(df.columns))), list(df.index))
