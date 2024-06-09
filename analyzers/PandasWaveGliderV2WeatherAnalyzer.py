import pandas as pd

from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather

from model.Table import Table


class PandasWaveGliderV2WeatherAnalyzer:

    def describe(self, weather: WaveGliderV2Weather) -> Table:
        described = self.__create_df(weather).describe()
        described.loc["mean", "TimeStamp"] = None
        return self.__create_table_from_df(described)

    def analyze_null_and_unique_values(self, weather: WaveGliderV2Weather) -> Table:
        df = self.__create_df(weather)
        return self.__create_table_from_df(pd.DataFrame({
            "Null_values": df.isna().sum(),
            "Unique values": df.nunique()
        }))

    def data_continuity(self, weather: WaveGliderV2Weather, count_threshold: int) -> Table:
        df = self.__create_df(weather)
        diff = self.__calculate_time_anomalies(df, count_threshold)
        return self.__create_table_from_df(pd.DataFrame(
            {"Difference": diff["TimeStamp"].reset_index(drop=True),
             "Previous TimeStamp": df.loc[diff.index - 1, "TimeStamp"].reset_index(drop=True),
             "Next TimeStamp": df.loc[diff.index, "TimeStamp"].reset_index(drop=True)}))

    def __calculate_time_anomalies(self, df: pd.DataFrame, count_threshold: int) -> pd.DataFrame:
        diff = df.diff(periods=1)
        value_counts = diff["TimeStamp"].value_counts().reset_index()
        return diff[diff["TimeStamp"].isin(value_counts[value_counts["count"] < count_threshold]["TimeStamp"])]


    def __create_df(self, weather: WaveGliderV2Weather) -> pd.DataFrame:
        return pd.DataFrame({
            "TimeStamp": weather.timestamp,
            "Temperature_C": weather.temperature_c,
            "Wind_speed_kt": weather.wind_speed_kt,
            "Wind_gust_speed_kt": weather.wind_gust_speed_kt,
            "Wind_direction": weather.wind_direction,
        })

    def __create_table_from_df(self, described: pd.DataFrame) -> Table:
        return Table(list(map(lambda label: Table.Column(label, list(described[label])), described.columns)),
                     list(described.index))
