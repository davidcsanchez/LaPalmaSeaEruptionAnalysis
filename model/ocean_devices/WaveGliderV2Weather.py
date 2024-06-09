from datetime import datetime


class WaveGliderV2Weather:

    def __init__(self, timestamp: list[datetime], temperature_c: list[float], wind_speed_kt: list[float],
                 wind_gust_speed_kt: list[float], wind_direction: list[float], latitude_deg: list[float],
                 longitude_deg: list[float]):
        self.index = list(range(len(timestamp)))
        self.timestamp = timestamp
        self.temperature_c = temperature_c
        self.wind_speed_kt = wind_speed_kt
        self.wind_gust_speed_kt = wind_gust_speed_kt
        self.wind_direction = wind_direction
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg

    def __eq__(self, other):
        return self.index == other.index and self.timestamp == other.timestamp and\
            self.temperature_c == other.temperature_c and self.wind_speed_kt == other.wind_speed_kt and \
            self.wind_direction == self.wind_direction and self.latitude_deg == other.latitude_deg and \
            self.longitude_deg == other.longitude_deg and self.wind_gust_speed_kt == self.wind_gust_speed_kt
