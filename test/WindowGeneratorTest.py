import unittest
from datetime import datetime

from machine_learning.model_preprocessors.DataWindowManager import DataWindowManager


class WindowGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.window_generator = DataWindowManager()

    def test_generate_temperature_daily_window(self):
        base = datetime(year=2023, month=12, day=31)
        oc_temp = [19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8, 19.9, 20.0,
                   20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9, 21.0,
                   21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9, 22.0,
                   22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9, 23.0,
                   23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7, 23.8, 23.9, 24.0,
                   24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.8, 24.9, 25.0,
                   24.9, 24.8, 24.7, 24.6, 24.5, 24.4, 24.3, 24.2, 24.1, 24.0,
                   23.9, 23.8, 23.7, 23.6]
        weather_temp = [19.0, 19.1, 19.4, 19.6, 20.0, 20.3, 20.5, 20.8, 21.2, 21.5,
                        21.7, 22.0, 22.4, 22.7, 22.9, 23.1, 23.5, 23.8, 24.0, 24.4,
                        24.6, 24.9, 25.0, 24.7, 24.3, 24.1, 23.9, 23.6, 23.2, 22.9,
                        22.6, 22.4, 22.0, 21.7, 21.5, 21.2, 21.0, 20.7, 20.4, 20.2,
                        20.0, 19.7, 19.5, 19.2, 19.0, 18.7, 18.5, 18.2, 18.0, 17.7,
                        17.5, 17.2, 17.0, 16.7, 16.5, 16.2, 16.0, 15.7, 15.5, 15.2,
                        15.0, 14.7, 14.5, 14.2, 14.0, 13.7, 13.5, 13.2, 13.0, 13.7,
                        13.5, 13.2, 13.0, 13.2]
        ocean_1_real_result = [oc_temp[i * 24:(i + 1) * 24] for i in range(len(oc_temp) // 24)]
        weather_2_real_result = [weather_temp[i * 24:(i + 1) * 24] for i in range(len(weather_temp) // 24)]
        x, y = self.window_generator.generate_window(24, weather_temp, oc_temp)
        self.assertEqual(x, weather_2_real_result)
        self.assertEqual(y, ocean_1_real_result)
