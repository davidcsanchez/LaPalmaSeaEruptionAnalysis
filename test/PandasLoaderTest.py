import unittest
from datetime import datetime

import geopandas as gpd
import pandas as pd
import pandas.testing as pdt

from etl.loaders.GeoPandasMapLoader import GeoPandasMapLoader
from etl.loaders.PandasSpikesLoader import PandasSpikesLoader
from etl.loaders.PandasWaveGliderV2OceanLoader import PandasWaveGliderV2OceanLoader
from etl.loaders.PandasSeabedLoader import PandasSeabedLoader
from etl.loaders.PandasWaveGliderWeatherLoader import PandasWaveGliderWeatherLoader
from model.Spikes import Spikes
from model.ocean_devices.Seabed import Seabed
from model.ocean_devices.WaveGliderV2Ocean import WaveGliderV2Ocean
from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather


class PandasLoaderTest(unittest.TestCase):

    def test_load_geo_pandas_map(self):
        gdf = gpd.read_file("resources/test.geojson")
        geo_pandas_map = GeoPandasMapLoader().load(gdf)
        pdt.assert_frame_equal(geo_pandas_map.data, gdf)

    def test_load_seabed(self):
        timestamps = [datetime(2024, 4, 10, 9, 5, 0),
                      datetime(2024, 5, 10, 10, 0, 0),
                      datetime(2024, 6, 10, 11, 15, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]

        temperature_c = [25.0, 26.5, 27.8, 24.3]
        conductivity_s_m = [0.05, 0.06, 0.055, 0.07]
        salinity_psu = [35.5, 36.2, 35.8, 34.9]
        df = pd.DataFrame({
            'TimeStamp': timestamps,
            'Temperature_C': temperature_c,
            'Conductivity_S_m': conductivity_s_m,
            'Salinity_PSU': salinity_psu
        })
        seabed_real = Seabed(timestamps, temperature_c, conductivity_s_m, salinity_psu)
        seabed = PandasSeabedLoader().load(df)
        self.assertEqual(seabed_real, seabed)

    def test_load_glider(self):
        timestamps = [datetime(2024, 4, 10, 9, 5, 0),
                      datetime(2024, 5, 10, 10, 0, 0),
                      datetime(2024, 6, 10, 11, 15, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]
        temperature_c = [25.0, 26.5, 27.8, 24.3]
        conductivity_s_m = [0.05, 0.06, 0.055, 0.07]
        salinity_psu = [35.5, 36.2, 35.8, 34.9]
        pressure_d = [1010.0, 1010.5, 1011.0, 1011.5]
        oxygen = [7.8, 8.2, 7.5, 8.0]
        latitude_deg = [40.7128, 51.5074, 35.6895, -33.8688]
        longitude_deg = [-74.0060, -0.1278, 139.6917, 151.2093]
        df = pd.DataFrame({
            'TimeStamp': timestamps,
            'Temperature_C': temperature_c,
            'Conductivity_S_m': conductivity_s_m,
            'Salinity_PSU': salinity_psu,
            'Pressure_d': pressure_d,
            'Oxygen_umol_L': oxygen,
            'Latitude_deg': latitude_deg,
            'Longitude_deg': longitude_deg
        })

        glider_real = WaveGliderV2Ocean(timestamps, temperature_c, conductivity_s_m, salinity_psu, pressure_d, oxygen,
                                        latitude_deg,
                                        longitude_deg)
        glider = PandasWaveGliderV2OceanLoader().load(df)
        self.assertEqual(glider_real, glider)

    def test_load_weather(self):
        timestamps = [datetime(2024, 4, 10, 9, 5, 0),
                      datetime(2024, 5, 10, 10, 0, 0),
                      datetime(2024, 6, 10, 11, 15, 0),
                      datetime(2024, 7, 10, 12, 30, 0)]

        temperature_c = [25.0, 26.5, 27.8, 24.3]
        wind_speed_kt = [10.2, 12.5, 8.7, 15.0]
        wind_gust_speed_kt = [15.0, 18.3, 14.2, 20.5]
        wind_direction = [120.0, 145.0, 105.0, 170.0]
        latitude_deg = [40.7128, 51.5074, 35.6895, -33.8688]
        longitude_deg = [-74.0060, -0.1278, 139.6917, 151.2093]
        df = pd.DataFrame({
            'TimeStamp': timestamps,
            'Temperature_C': temperature_c,
            'Wind_speed_kt': wind_speed_kt,
            'Wind_gust_speed_kt': wind_gust_speed_kt,
            'Wind_direction': wind_direction,
            'Latitude_deg': latitude_deg,
            'Longitude_deg': longitude_deg
        })
        weather_real = WaveGliderV2Weather(timestamps, temperature_c, wind_speed_kt, wind_gust_speed_kt, wind_direction,
                                           latitude_deg, longitude_deg)
        weather = PandasWaveGliderWeatherLoader().load(df)
        self.assertEqual(weather, weather_real)

    def test_load_spikes(self):
        df = pd.DataFrame({
            'Variable': ['Salinity_PSU', 'Salinity_PSU', 'Salinity_PSU'],
            'Threshold': [0.084, 0.084, 0.084],
            'TimeStamp': ['09/02/2022 01:46', '24/02/2022 07:54', '09/03/2022 13:02'],
            'Values': [36.591, 36.671, 37.060]
        }, index=[1209, 5885, 9967])
        df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format='%d/%m/%Y %H:%M')
        spikes = PandasSpikesLoader().load(df)
        real_sal_spikes = Spikes(
            [Spikes.SpikeVariable.SALINITY_PSU] * 3,
                                 0.084,
            list(pd.to_datetime(['09/02/2022 01:46', '24/02/2022 07:54', '09/03/2022 13:02'], format='%d/%m/%Y %H:%M')),
            [36.591, 36.671, 37.060],
            [1209, 5885, 9967])
        self.assertEqual(spikes.to_table(), real_sal_spikes.to_table())
