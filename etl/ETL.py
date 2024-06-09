from datetime import timedelta
from typing import Callable, Iterable, Any, Self

from model.Spikes import Spikes


class ETL:

    def __init__(self, extractor, transformer, loader):
        self.data = None
        self.extractor = extractor
        self.transformer = transformer
        self.loader = loader

    def extract(self, path: str) -> Self:
        self.data = self.extractor.extract(path)
        return self

    def rename_columns(self, old_and_new_names: dict[str, str]) -> Self:
        self.data = self.transformer.rename_columns(self.data, old_and_new_names)
        return self

    def sort_values(self, column_label: str) -> Self:
        self.data = self.transformer.sort_values(self.data, column_label)
        return self

    def correct_dates(self, greater_than: any, less_than: any, col_name: str,
                      time_to_subtract: timedelta) -> Self:
        self.data = self.transformer.correct_dates(self.data, greater_than, less_than, col_name, time_to_subtract)
        return self

    def filter_column(self, col_name: str, operator: Callable, value: any) -> Self:
        self.data = self.transformer.filter_column(self.data, col_name, operator, value)
        return self

    def filter_column_and_interpolate(self, col_name: str, operator: Callable, value: any) -> Self:
        self.data = self.transformer.filter_column_and_interpolate(self.data, col_name, operator, value)
        return self

    def concat_data(self, etl_with_data_to_concat: Self) -> Self:
        self.data = self.transformer.concat_data(self.data, etl_with_data_to_concat.data)
        return self

    def add_column(self, label: str, values: Iterable[Any]) -> Self:
        self.data = self.transformer.add_column(self.data, label, values)
        return self

    def compute_average_per_timestamp(self, date_col: str) -> Self:
        self.data = self.transformer.compute_average_per_timestamp(self.data, date_col)
        return self

    def compute_average_per_day_hour(self, date_column: str) -> Self:
        self.data = self.transformer.compute_average_per_day_hour(self.data, date_column)
        return self

    def remove_values_not_in(self, col_with_values: str, etl_with_values_to_keep: Self) -> Self:
        self.data = self.transformer.remove_values_not_in(self.data, col_with_values, etl_with_values_to_keep.data)
        return self

    def merge_columns(self, columns: list[str], new_column: str, sep_value: str) -> Self:
        self.data = self.transformer.merge_columns(self.data, columns, new_column, sep_value)
        return self

    def parse_datetime_column(self, time_column: str, date_format: str = None) -> Self:
        self.data = self.transformer.parse_datetime_column(self.data, time_column, date_format)
        return self

    def interpolate_outliers(self, outliers: Spikes, timestamps_label: str) -> Self:
        self.data = self.transformer.interpolate_outliers(self.data, outliers, timestamps_label)
        return self

    def load(self):
        return self.loader.load(self.data)
