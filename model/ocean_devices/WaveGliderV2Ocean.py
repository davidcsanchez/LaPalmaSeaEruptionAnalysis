from datetime import datetime


class WaveGliderV2Ocean:
    def __init__(self, timestamp: list[datetime], temperature_c: list[float], conductivity_s_m: list[float],
                 salinity_psu: list[float],
                 pressure_d: list[float], oxygen: list[float], latitude_deg: list[float], longitude_deg: list[float]):
        self.oxygen = oxygen
        self.index = list(range(len(timestamp)))
        self.timestamp = timestamp
        self.temperature_c = temperature_c
        self.conductivity_s_m = conductivity_s_m
        self.salinity_psu = salinity_psu
        self.pressure_d = pressure_d
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.temperature_c == other.temperature_c and \
            self.conductivity_s_m == other.conductivity_s_m and \
            self.salinity_psu == other.salinity_psu and \
            self.pressure_d == other.pressure_d and self.latitude_deg == other.latitude_deg and \
            self.longitude_deg == other.longitude_deg and \
            self.oxygen == other.oxygen and self.index == other.index
