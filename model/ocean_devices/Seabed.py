from datetime import datetime


class Seabed:
    def __init__(self, timestamp: list[datetime], temperature_c: list[float], conductivity_s_m: list[float],
                 salinity_psu: list[float]):
        self.index = list(range(len(timestamp)))
        self.timestamp = timestamp
        self.temperature_c = temperature_c
        self.conductivity_s_m = conductivity_s_m
        self.salinity_psu = salinity_psu

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.temperature_c == other.temperature_c and \
            self.conductivity_s_m == other.conductivity_s_m and \
            self.salinity_psu == other.salinity_psu and \
            self.index == other.index
