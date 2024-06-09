from copy import deepcopy


class Table:
    class Column:
        def __init__(self, label: str, values: list) -> None:
            self.label = label
            self.values = values

        def __eq__(self, other):
            are_equal = self.label == other.label and self.values == other.values
            return self.label == other.label and self.values == other.values

    def __init__(self, columns: list[Column], indexes: list = None) -> None:
        self.columns = columns
        self.indexes = indexes

    def concat_equal_tables(self, table_2: "Table") -> "Table":
        result_table = deepcopy(self)
        if self.indexes is None:
            result_table.indexes = table_2.indexes
        elif table_2.indexes is not None:
            result_table.indexes.extend(table_2.indexes)
        table_2_labels = [column.label for column in table_2.columns]
        for column in result_table.columns:
            if column.label in table_2_labels:
                column.values.extend(self.__get_column_from_label(table_2, column.label))
        return result_table

    def __get_column_from_label(self, table: "Table", label: str) -> list:
        for column in table.columns:
            if column.label == label:
                return column.values

    def __eq__(self, other):
        return self.__compare_all_columns(other) and (self.indexes == other.indexes)

    def __compare_all_columns(self, other):
        self.columns.sort(key=lambda x: x.label, reverse=True)
        other.columns.sort(key=lambda x: x.label, reverse=True)
        return all([col_1 == col_2 for col_1, col_2 in zip(self.columns, other.columns)])
