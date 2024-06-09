import os
from typing import Self

import pandas as pd
from model.Table import Table


class CsvPandasStorer:

    def __init__(self, number_of_decimals: int = 2, format_dict: dict[str, str] = None):
        self.format_dict = format_dict
        self.float_format = '%.' + str(number_of_decimals + 1) + 'f'

    def store(self, table: Table, filename: str, date_format: str | None, index: bool, translate: bool = False,
              labels_to_translate: list[str] = None) -> Self:
        self.__create_dir_if_not_exists(filename)
        if translate:
            self.__translate_labels(table, labels_to_translate)
        df = self.__table_to_df(table)
        df.to_csv(filename, index=index, date_format=date_format, float_format=self.float_format)
        return self

    def __create_dir_if_not_exists(self, filename) -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

    def __table_to_df(self, table: Table) -> pd.DataFrame:
        return pd.DataFrame(index=table.indexes, data=dict(map(lambda label, values: (label, values),
                                                               map(lambda col: col.label, table.columns),
                                                               map(lambda col: col.values, table.columns))))

    def __translate_labels(self, table, labels_to_translate) -> None:
        for column in [column for column in table.columns]:
            if column.label in labels_to_translate:
                column.values = [self.format_dict[value] for value in column.values]
        if "indexes" in labels_to_translate:
            table.indexes = [self.format_dict[index] for index in table.indexes]
