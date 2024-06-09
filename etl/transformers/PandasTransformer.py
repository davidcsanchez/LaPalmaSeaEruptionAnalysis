from datetime import timedelta, datetime
import operator
from typing import Callable, Iterable, Any

import pandas as pd

from model.Spikes import Spikes


class PandasTransformer:

    def rename_columns(self, df: pd.DataFrame, old_and_new_names: dict[str, str]) -> pd.DataFrame:
        return df.rename(columns=old_and_new_names, inplace=False)

    def sort_values(self, df: pd.DataFrame, column_label: str) -> pd.DataFrame:
        return df.sort_values(column_label).reset_index(drop=True)

    def correct_dates(self, df: pd.DataFrame, greater_than: any, less_than: any, col_name: str,
                      time_to_subtract: timedelta) -> pd.DataFrame:
        idx = self.__limit_column_idx(df, col_name, greater_than, less_than)
        df.loc[idx, col_name] = df[idx][col_name] - time_to_subtract
        return df

    def __limit_column_idx(self, df: pd.DataFrame, col: str, greater_than: any, less_than: any) -> pd.Series:
        return (self.__filter_idx_column(df, col, operator.ge, greater_than) &
                self.__filter_idx_column(df, col, operator.le, less_than))

    def filter_column(self, df: pd.DataFrame, col_name: str, filter_operator: Callable, value: any) -> pd.DataFrame:
        return df[self.__filter_idx_column(df, col_name, filter_operator, value)].reset_index(drop=True)

    def filter_column_and_interpolate(self, df: pd.DataFrame, col_name: str, filter_operator: Callable,
                                      value: any) -> pd.DataFrame:
        df.loc[~self.__filter_idx_column(df, col_name, filter_operator, value), col_name] = None
        return df.interpolate(method='linear', axis=0).reset_index(drop=True)

    def concat_data(self, df_1: pd.DataFrame, df_2: pd.DataFrame) -> pd.DataFrame:
        return pd.concat([df_1, df_2])

    def add_column(self, df: pd.DataFrame, label: str, values: Iterable[Any]) -> pd.DataFrame:
        df[label] = values
        return df

    def __filter_idx_column(self, df: pd.DataFrame, col: str, filter_operator: Callable, value: any) -> pd.Series:
        return filter_operator(df[col], value)

    def compute_average_per_timestamp(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        df[date_column] = df[date_column].dt.strftime('%H:%M')
        return df.groupby(date_column).mean().reset_index()

    def compute_average_per_day_hour(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        return self.__mean_by_hour(date_column, df)

    def __mean_by_hour(self, date_column: str, df: pd.DataFrame) -> pd.DataFrame:
        df[date_column] = df[date_column].dt.strftime('%d/%m/%Y %H')
        df = df.groupby(date_column).mean()
        df.index = pd.to_datetime(df.index, format='%d/%m/%Y %H')
        df = df.reindex(pd.date_range(min(df.index), end=max(df.index), freq='1h'))
        df = self.__calculate_missing_hours(df, date_column)
        return df

    def remove_values_not_in(self, df: pd.DataFrame, col_with_values: str, values_to_keep: pd.DataFrame) \
            -> pd.DataFrame:
        return df[df[col_with_values].isin(values_to_keep[col_with_values])]

    def __calculate_missing_hours(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        df["Hora del día"] = df.index.strftime('%H')
        df.index.name = date_column
        df.reset_index(inplace=True)
        for day_hour in df["Hora del día"].unique():
            if df.loc[df["Hora del día"] == day_hour, :].isnull().values.any():
                df.loc[df["Hora del día"] == day_hour, :] = (df.loc[df["Hora del día"] == day_hour, :]
                                                             .sort_values([date_column], ascending=True).
                                                             ffill(inplace=False))
                df.loc[df["Hora del día"] == day_hour, :] = (df.loc[df["Hora del día"] == day_hour, :]
                                                             .sort_values([date_column], ascending=False)
                                                             .ffill(inplace=False))
        return df.drop(["Hora del día"], axis=1)

    def merge_columns(self, df: pd.DataFrame, columns: list[str], new_column: str, sep_value: str) -> pd.DataFrame:
        df[new_column] = df[columns].astype(str).agg(sep_value.join, axis=1)
        return df.drop(columns, axis=1)

    def parse_datetime_column(self, df: pd.DataFrame, time_column: str, date_format: str = None) -> pd.DataFrame:
        df[time_column] = pd.to_datetime(df[time_column], format=date_format)
        return df

    def interpolate_outliers(self, df: pd.DataFrame, outliers: Spikes, timestamps_label: str) -> pd.DataFrame:
        spikes_df = self.__spikes_to_df(outliers)
        for variable in spikes_df["Variable"].unique():
            df.loc[df[timestamps_label].isin(
                spikes_df[spikes_df["Variable"] == variable][timestamps_label]), variable] = None
        return df.interpolate(method='linear', axis=0)

    def __spikes_to_df(self, outliers: Spikes) -> pd.DataFrame:
        return pd.DataFrame({"Variable": [value.value for value in outliers.variable],
                             "TimeStamp": outliers.timestamp,
                             "Threshold": [outliers.threshold] * len(outliers.timestamp)},
                            index=outliers.indexes)
