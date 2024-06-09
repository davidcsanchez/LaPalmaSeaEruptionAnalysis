import os
import unittest
from datetime import datetime

import pandas as pd

from model.Table import Table
from storer.CsvPandasStorer import CsvPandasStorer
import pandas.testing as pdt

from storer.MatplotlibFigureStorer import MatplotlibFigureStorer


class StorerTest(unittest.TestCase):

    def setUp(self):
        self.csv_storer = CsvPandasStorer()
        self.figure_storer = MatplotlibFigureStorer()

    def test_pandas_storer(self):
        table = self.__get_weather_table()
        self.csv_storer.store(table, "./resources/stored.csv", None, False)
        loaded = pd.read_csv("resources/stored.csv", parse_dates=["TimeStamp"])
        pdt.assert_frame_equal(self.__get_weather_df(), loaded)

    def test_jpg_storer(self):
        path = "resources/figura1.jpg"
        self.figure_storer.store(path)
        self.assertTrue(os.path.isfile(path))

    def __get_weather_table(self) -> Table:
        timestamps = [datetime(2024, 7, 10, 9, 5, 0),
                      datetime(2024, 7, 10, 9, 10, 0),
                      datetime(2024, 7, 10, 9, 15, 0),
                      datetime(2024, 7, 10, 9, 20, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]

        temperature_c = [25.0, 26.5, 27.8, 24.3, 24.33]
        wind_speed_kt = [10.2, 12.5, 8.7, 15.0, 15.03]
        wind_gust_speed_kt = [15.0, 18.3, 14.2, 20.5, 20.54]
        wind_direction = [120.0, 145.0, 105.0, 170.0, 170.054]
        latitude_deg = [40.718, 51.574, 35.695, -33.888, -33.812]
        longitude_deg = [-74.060, -0.178, 139.697, 151.203, 151.209]
        return Table([
            Table.Column('TimeStamp', timestamps),
            Table.Column("Temperatura Cº", temperature_c),
            Table.Column("Velocidad del viento kt", wind_speed_kt),
            Table.Column("Velocidad ráfagas de viento kt", wind_gust_speed_kt),
            Table.Column("Dirección del viento", wind_direction),
            Table.Column("Latitude", latitude_deg),
            Table.Column("Longitude", longitude_deg)
        ])

    def __get_weather_df(self) -> pd.DataFrame:
        timestamps = [datetime(2024, 7, 10, 9, 5, 0),
                      datetime(2024, 7, 10, 9, 10, 0),
                      datetime(2024, 7, 10, 9, 15, 0),
                      datetime(2024, 7, 10, 9, 20, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]

        temperature_c = [25.0, 26.5, 27.8, 24.3, 24.33]
        wind_speed_kt = [10.2, 12.5, 8.7, 15.0, 15.03]
        wind_gust_speed_kt = [15.0, 18.3, 14.2, 20.5, 20.54]
        wind_direction = [120.0, 145.0, 105.0, 170.0, 170.054]
        latitude_deg = [40.718, 51.574, 35.695, -33.888, -33.812]
        longitude_deg = [-74.060, -0.178, 139.697, 151.203, 151.209]
        return pd.DataFrame({
            'TimeStamp': timestamps,
            "Temperatura Cº": temperature_c,
            "Velocidad del viento kt": wind_speed_kt,
            "Velocidad ráfagas de viento kt": wind_gust_speed_kt,
            "Dirección del viento": wind_direction,
            "Latitude": latitude_deg,
            "Longitude": longitude_deg
        })
