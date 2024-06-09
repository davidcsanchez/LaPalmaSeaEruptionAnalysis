import pandas as pd


class CSVPandasExtractor:

    def __init__(self, parse_dates: list[str] = None, date_format: str = None,
                 relevant_cols_idx: list[int] = None, delimiter: str = None, index_col: list[int] = False):
        self.parse_dates = parse_dates
        self.date_format = date_format
        self.relevant_cols_idx = relevant_cols_idx
        self.delimiter = delimiter
        self.index_col = index_col

    def extract(self, csv: str) -> pd.DataFrame:
        if self.parse_dates is None:
            return pd.read_csv(csv, usecols=self.relevant_cols_idx, delimiter=self.delimiter, index_col=self.index_col)
        return (pd.read_csv(csv, parse_dates=self.parse_dates, date_format=self.date_format, delimiter=self.delimiter,
                            usecols=self.relevant_cols_idx, index_col=self.index_col))
