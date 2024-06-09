import unittest
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from numpy import cov
from scipy.stats import spearmanr, pearsonr

from analyzers.NumpyPrimitiveDataAnalyzer import NumpyPrimitiveDataAnalyzer
from analyzers.PandasWaveGliderV2OceanAnalyzer import PandasWaveGliderV2OceanAnalyzer
from analyzers.PandasSeabedAnalyzer import PandasSeabedAnalyzer
from analyzers.PandasWaveGliderV2WeatherAnalyzer import PandasWaveGliderV2WeatherAnalyzer
import numpy.testing as npt

from analyzers.SciPyCorrelationAnalyzer import SciPyCorrelationAnalyzer
from model.ocean_devices.Seabed import Seabed
from model.Table import Table
from model.ocean_devices.WaveGliderV2Ocean import WaveGliderV2Ocean
from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather
from model.params.CorrelationInput import CorrelationInput


class PandasAnalyzerTest(unittest.TestCase):

    def setUp(self):
        self.glider_analyzer = PandasWaveGliderV2OceanAnalyzer()
        self.seabed_analyzer = PandasSeabedAnalyzer()
        self.weather_analyzer = PandasWaveGliderV2WeatherAnalyzer()

    def test_weather_analyzer(self):
        weather_df, weather = self.__get_weather_data()
        described = self.weather_analyzer.describe(weather)
        table = self.__create_table_from_df(self.__pandas_describe(weather_df))
        self.assertEqual(described, table)

        anomalies_table = self.weather_analyzer.analyze_null_and_unique_values(weather)

        null_values, unique_values = self.__get_anomalies_values(anomalies_table)
        npt.assert_array_equal(null_values, np.array([0] * 5))
        npt.assert_array_equal(unique_values, np.array([5] * 5))

        continuity = self.weather_analyzer.data_continuity(weather, 3)
        continuity_real = Table([
            Table.Column("Difference", [timedelta(hours=3, minutes=10)]),
            Table.Column("Previous TimeStamp", [pd.to_datetime("2024-07-10 09:20:00")]),
            Table.Column("Next TimeStamp", [pd.to_datetime("2024-07-10 12:30:00")])
        ], indexes=[0])
        self.assertEqual(continuity, continuity_real)

    def __get_anomalies_values(self, table):
        null_values = next((col.values for col in table.columns if col.label == "Null_values"), None)
        unique_values = next((col.values for col in table.columns if col.label != "Null_values"), None)
        return null_values, unique_values

    def __pandas_describe(self, df):
        df = df.describe()
        df.loc["mean", "TimeStamp"] = None
        return df

    def test_seabed_analyzer(self):
        seabed_df, seabed = self.__get_seabed_data()
        described = self.seabed_analyzer.describe(seabed)
        self.assertEqual(described, self.__create_table_from_df(self.__pandas_describe(seabed_df)))

        null_values, unique_values = self.__get_anomalies_values(self.seabed_analyzer.analyze_null_and_unique_values(seabed))
        npt.assert_array_equal(null_values, np.array([0] * 4))
        npt.assert_array_equal(unique_values, np.array([5] * 4))

        continuity = self.seabed_analyzer.data_continuity(seabed, 3)
        continuity_real = Table([
            Table.Column("Difference", [timedelta(hours=3, minutes=10)]),
            Table.Column("Previous TimeStamp", [pd.to_datetime("2024-07-10 09:20:00")]),
            Table.Column("Next TimeStamp", [pd.to_datetime("2024-07-10 12:30:00")])
        ], indexes=[0])
        self.assertEqual(continuity, continuity_real)

        spikes = PandasSeabedAnalyzer(seabed).analyze_outliers_salinity(seabed)
        self.assertEqual(0, len(spikes.values))

    def test_glider_analyzer(self):
        glider_df, glider = self.__get_glider_data()
        described = self.glider_analyzer.describe(glider)
        described_real = self.__create_table_from_df(self.__pandas_describe(glider_df))
        self.assertEqual(described, described_real)

        null_values, unique_values = self.__get_anomalies_values(self.glider_analyzer.analyze_null_and_unique_values(glider))
        npt.assert_array_equal(null_values, np.array([0] * 6))
        npt.assert_array_equal(unique_values, np.array([5] * 6))

        continuity = self.glider_analyzer.data_continuity(glider, 3)
        continuity_real = Table([
            Table.Column("Difference", [timedelta(hours=3, minutes=10)]),
            Table.Column("Previous TimeStamp", [pd.to_datetime("2024-07-10 09:20:00")]),
            Table.Column("Next TimeStamp", [pd.to_datetime("2024-07-10 12:30:00")])
        ], indexes=[0])
        self.assertEqual(continuity, continuity_real)

        spikes = PandasWaveGliderV2OceanAnalyzer(glider).analyze_outliers_salinity(glider)
        self.assertEqual(0, len(spikes.values))
        spikes = PandasWaveGliderV2OceanAnalyzer(glider).analyze_outliers_oxygen(glider)
        self.assertEqual([8.2, 7.5], spikes.values)


    def test_primitive_data_analyzer(self):
        values = [36.591, 36.671, 37.060, 142.226, 120.984, 78.312, 34.679, 56.789, 90.123, 45.678]
        real_result = (-38.83475000000001, 36.76825, 87.17025000000001, 162.77325000000002)
        result = NumpyPrimitiveDataAnalyzer().analyze_intercuartilic_thresholds(values)
        self.assertEqual(real_result, result)

    def test_correlation_analyzer(self):
        input_data = CorrelationInput([1, 2, 3], [1, 2, 3], "test")
        expected_covariance = cov([1, 2, 3], [1, 2, 3])[1][1]
        expected_pearson = pearsonr([1, 2, 3], [1, 2, 3])[0]
        expected_pearson_p_value = pearsonr([1, 2, 3], [1, 2, 3])[1]
        expected_spearman = spearmanr([1, 2, 3], [1, 2, 3])[0]
        expected_spearman_p_value = spearmanr([1, 2, 3], [1, 2, 3])[1]

        expected_table = Table(
            [
                Table.Column("Covariance", [expected_covariance]),
                Table.Column("Pearson", [expected_pearson]),
                Table.Column("Pearson p-valor", [expected_pearson_p_value]),
                Table.Column("Pearson p-valor adjusted", [expected_pearson_p_value]),
                Table.Column("Spearman", [expected_spearman]),
                Table.Column("Spearman p-valor", [expected_spearman_p_value]),
                Table.Column("Spearman p-valor adjusted", [expected_spearman_p_value]),
            ],
            ["test"]
        )

        result = SciPyCorrelationAnalyzer().analyze([input_data])

        self.assertEqual(result, expected_table)


    def __get_glider_data(self):
        timestamps = [datetime(2024, 7, 10, 9, 5, 0),
                      datetime(2024, 7, 10, 9, 10, 0),
                      datetime(2024, 7, 10, 9, 15, 0),
                      datetime(2024, 7, 10, 9, 20, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]
        temperature_c = [25.0, 26.5, 27.8, 24.3, 24.43]
        conductivity_s_m = [0.05, 0.06, 0.055, 0.07, 0.047]
        salinity_psu = [35.5, 36.2, 35.8, 34.9, 34.49]
        pressure_d = [1010.0, 1010.5, 1011.0, 1011.5, 1011.45]
        oxygen = [7.8, 8.2, 7.5, 8.0, 8.04]
        latitude_deg = [40.7128, 51.5074, 35.6895, -33.8688, -33.86884]
        longitude_deg = [-74.0060, -0.1278, 139.6917, 151.2093, 151.24093]
        df = pd.DataFrame({
            'TimeStamp': timestamps,
            'Temperature_C': temperature_c,
            'Conductivity_S_m': conductivity_s_m,
            'Salinity_PSU': salinity_psu,
            'Pressure_d': pressure_d,
            'Oxygen_umol_L': oxygen
        })
        wave_glider = WaveGliderV2Ocean(timestamps, temperature_c, conductivity_s_m, salinity_psu, pressure_d, oxygen,
                                        latitude_deg,
                                        longitude_deg)
        return df, wave_glider

    def __get_seabed_data(self):
        timestamps = [datetime(2024, 7, 10, 9, 5, 0),
                      datetime(2024, 7, 10, 9, 10, 0),
                      datetime(2024, 7, 10, 9, 15, 0),
                      datetime(2024, 7, 10, 9, 20, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]

        temperature_c = [25.0, 26.5, 27.8, 24.3, 24.33]
        conductivity_s_m = [0.05, 0.06, 0.055, 0.07, 0.072]
        salinity_psu = [35.5, 36.2, 35.8, 34.9, 34.934]
        df = pd.DataFrame({
            'TimeStamp': timestamps,
            'Temperature_C': temperature_c,
            'Conductivity_S_m': conductivity_s_m,
            'Salinity_PSU': salinity_psu
        })
        seabed = Seabed(timestamps, temperature_c, conductivity_s_m, salinity_psu)
        return df, seabed

    def __get_weather_data(self):
        timestamps = [datetime(2024, 7, 10, 9, 5, 0),
                      datetime(2024, 7, 10, 9, 10, 0),
                      datetime(2024, 7, 10, 9, 15, 0),
                      datetime(2024, 7, 10, 9, 20, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]

        temperature_c = [25.0, 26.5, 27.8, 24.3, 24.33]
        wind_speed_kt = [10.2, 12.5, 8.7, 15.0, 15.03]
        wind_gust_speed_kt = [15.0, 18.3, 14.2, 20.5, 20.54]
        wind_direction = [120.0, 145.0, 105.0, 170.0, 170.054]
        latitude_deg = [40.7128, 51.5074, 35.6895, -33.8688, -33.868812]
        longitude_deg = [-74.0060, -0.1278, 139.6917, 151.2093, 151.2093132]
        df = pd.DataFrame({
            'TimeStamp': timestamps,
            "Temperature_C": temperature_c,
            "Wind_speed_kt": wind_speed_kt,
            "Wind_gust_speed_kt": wind_gust_speed_kt,
            "Wind_direction": wind_direction,
        })

        weather = WaveGliderV2Weather(timestamps, temperature_c, wind_speed_kt, wind_gust_speed_kt, wind_direction,
                                      latitude_deg, longitude_deg)
        return df, weather

    def __create_table_from_df(self, df: pd.DataFrame) -> Table:
        df.loc["mean", "TimeStamp"] = None
        return Table(list(map(lambda label: Table.Column(label, list(df[label])), df.columns)), list(df.index))
