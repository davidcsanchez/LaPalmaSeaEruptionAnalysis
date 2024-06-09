from datetime import datetime

from model.Table import Table
from enum import StrEnum


class Spikes:

    class SpikeVariable(StrEnum):
        SALINITY_PSU = "Salinity_PSU"
        OXYGEN_UMOL_L = "Oxygen_umol_L"

    def __init__(self, variable: list[SpikeVariable], threshold: float, timestamp: list[datetime], values: list[float], indexes: list[int]):
        self.variable = variable
        self.threshold = threshold
        self.timestamp = timestamp
        self.values = values
        self.indexes = indexes

    def to_table(self) -> Table:
        return Table(
            [
                Table.Column("Variable", self.variable),
                Table.Column("Threshold", [self.threshold] * len(self.indexes)),
                Table.Column("TimeStamp", self.timestamp),
                Table.Column("Values", self.values),
            ],
            self.indexes
        )
