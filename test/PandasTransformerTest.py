import operator
import unittest
from datetime import timedelta

import numpy as np
import numpy.testing as npt
import pandas.testing as pdt
import pandas as pd

from etl.transformers.PandasTransformer import PandasTransformer
from model.Spikes import Spikes
from model.Table import Table


class PandasTransformerTest(unittest.TestCase):

    def setUp(self):
        self.transformer = PandasTransformer()
        self.data = pd.DataFrame({
            'TimeStamp': [
                pd.to_datetime('2024-03-09 12:00:00'),
                pd.to_datetime('2024-03-09 12:05:00'),
                pd.to_datetime('2024-03-09 12:10:00'),
                pd.to_datetime('2024-03-09 12:15:00'),
                pd.to_datetime('2024-03-09 12:20:00'),
                pd.to_datetime('2024-03-09 12:25:00'),
                pd.to_datetime('2024-03-09 12:30:00'),
                pd.to_datetime('2024-03-09 12:35:00'),
                pd.to_datetime('2024-03-09 12:40:00'),
                pd.to_datetime('2024-03-09 12:45:00')
            ],
            'Latitude_deg': [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45],
            'Longitude_deg': [-180, -150, -120, -90, -60, -30, 0, 30, 60, 90],
            'Pressure_d': [1005.0, 1004.5, 1004.0, 1003.5, 1003.0, 1002.5, 1002.0, 1001.5, 1001.0, 1000.5],
            'Temperature_C': [25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0],
            'Conductivity_S_m': [0.03, 0.032, 0.034, 0.036, 0.038, 0.04, 0.042, 0.044, 0.046, 0.048],
            'Oxygen': [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5],
            'Salinity_PSU': [32.0, 32.5, 33.0, 33.5, 34.0, 34.5, 35.0, 35.5, 36.0, 36.5],
        })

    def test_filter_date_column(self):
        data_2 = self.transformer.filter_column(self.data, "TimeStamp",
                                                operator.lt, "2024-03-09 12:20:00")
        self.assertNotIn(pd.to_datetime('2024-03-09 12:45:00'), data_2["TimeStamp"].values)
        self.assertIn(pd.to_datetime('2024-03-09 12:05:00'), data_2["TimeStamp"].values)
        self.data = self.transformer.filter_column(self.data, "TimeStamp",
                                                   operator.gt, "2024-03-09 12:20:00")
        self.assertIn(pd.to_datetime('2024-03-09 12:45:00'), self.data["TimeStamp"].values)
        self.assertNotIn(pd.to_datetime('2024-03-09 12:05:00'), self.data["TimeStamp"].values)

    def test_rename_columns(self):
        renames = {"TimeStamp": "Time -_xX Stamp", "Conductivity_S_m": "conductivity"}
        old_col_data = self.data["TimeStamp"]
        self.data = self.transformer.rename_columns(self.data, renames)
        self.assertIn("Time -_xX Stamp", self.data.columns.values)
        self.assertIn("conductivity", self.data.columns.values)
        self.assertNotIn("TimeStamp", self.data.columns.values)
        self.assertNotIn("Conductivity_S_m", self.data.columns.values)
        new_col_data = self.data["Time -_xX Stamp"]
        npt.assert_array_equal(old_col_data.values, new_col_data.values)

    def test_correct_dates(self):
        self.transformer.correct_dates(self.data,
                                       "2024-03-09 12:20:00",
                                       "2024-03-09 12:40:00",
                                       "TimeStamp",
                                       timedelta(hours=0, minutes=3))
        self.assertNotIn(pd.to_datetime("2024-03-09 12:25:00"), self.data["TimeStamp"].values)
        self.assertNotIn(pd.to_datetime("2024-03-09 12:35:00"), self.data["TimeStamp"].values)
        self.assertIn(pd.to_datetime("2024-03-09 12:22:00"), self.data["TimeStamp"].values)
        self.assertIn(pd.to_datetime("2024-03-09 12:32:00"), self.data["TimeStamp"].values)
        self.assertIn(pd.to_datetime("2024-03-09 12:00:00"), self.data["TimeStamp"].values)
        self.assertIn(pd.to_datetime("2024-03-09 12:15:00"), self.data["TimeStamp"].values)
        self.assertIn(pd.to_datetime("2024-03-09 12:17:00"), self.data["TimeStamp"].values)
        self.assertIn(pd.to_datetime("2024-03-09 12:37:00"), self.data["TimeStamp"].values)
        self.assertNotIn(pd.to_datetime("2024-03-09 12:20:00"), self.data["TimeStamp"].values)
        self.assertNotIn(pd.to_datetime("2024-03-09 12:40:00"), self.data["TimeStamp"].values)

    def test_concat_data(self):
        data_2 = pd.DataFrame({
            'TimeStamp': [
                pd.to_datetime('2024-04-10 09:00:00'),
                pd.to_datetime('2024-04-10 09:05:00'),
                pd.to_datetime('2024-04-10 09:10:00'),
                pd.to_datetime('2024-04-10 09:15:00'),
                pd.to_datetime('2024-04-10 09:20:00'),
                pd.to_datetime('2024-04-10 09:25:00'),
                pd.to_datetime('2024-04-10 09:30:00'),
                pd.to_datetime('2024-04-10 09:35:00'),
                pd.to_datetime('2024-04-10 09:40:00'),
                pd.to_datetime('2024-04-10 09:45:00')
            ],
            'Latitude_deg': [50, 55, 60, 65, 70, 75, 80, 85, 90, 95],
            'Longitude_deg': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            'Pressure_d': [1010.0, 1010.5, 1011.0, 1011.5, 1012.0, 1012.5, 1013.0, 1013.5, 1014.0, 1014.5],
            'Temperature_C': [16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0],
            'Conductivity_S_m': [0.05, 0.052, 0.054, 0.056, 0.058, 0.06, 0.062, 0.064, 0.066, 0.068],
            'Oxygen': [6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8],
            'Salinity_PSU': [33, 33.5, 34, 34.5, 35, 35.5, 36, 36.5, 37, 37.5],
        })
        self.data_concatenated_real = self.get_data_concatenated()
        self.data_concatenated = self.transformer.concat_data(data_2, self.data).reset_index(drop=True)
        pdt.assert_frame_equal(self.data_concatenated, self.data_concatenated_real)

    def get_data_concatenated(self):
        return pd.DataFrame({
            'TimeStamp': [pd.to_datetime('2024-04-10 09:00:00'),
                          pd.to_datetime('2024-04-10 09:05:00'),
                          pd.to_datetime('2024-04-10 09:10:00'),
                          pd.to_datetime('2024-04-10 09:15:00'),
                          pd.to_datetime('2024-04-10 09:20:00'),
                          pd.to_datetime('2024-04-10 09:25:00'),
                          pd.to_datetime('2024-04-10 09:30:00'),
                          pd.to_datetime('2024-04-10 09:35:00'),
                          pd.to_datetime('2024-04-10 09:40:00'),
                          pd.to_datetime('2024-04-10 09:45:00'), pd.to_datetime('2024-03-09 12:00:00'),
                          pd.to_datetime('2024-03-09 12:05:00'),
                          pd.to_datetime('2024-03-09 12:10:00'),
                          pd.to_datetime('2024-03-09 12:15:00'),
                          pd.to_datetime('2024-03-09 12:20:00'),
                          pd.to_datetime('2024-03-09 12:25:00'),
                          pd.to_datetime('2024-03-09 12:30:00'),
                          pd.to_datetime('2024-03-09 12:35:00'),
                          pd.to_datetime('2024-03-09 12:40:00'),
                          pd.to_datetime('2024-03-09 12:45:00'),
                          ],
            'Latitude_deg': [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, -90, -75, -60, -45, -30, -15, 0, 15, 30, 45,
                             ],
            'Longitude_deg': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, -180, -150, -120, -90, -60, -30, 0, 30, 60, 90,
                              ],
            'Pressure_d': [1010.0, 1010.5, 1011.0, 1011.5, 1012.0, 1012.5, 1013.0, 1013.5, 1014.0, 1014.5, 1005.0,
                           1004.5, 1004.0, 1003.5, 1003.0, 1002.5, 1002.0, 1001.5, 1001.0, 1000.5,
                           ],
            'Temperature_C': [16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 25.0, 26.0, 27.0, 28.0, 29.0,
                              30.0, 31.0, 32.0, 33.0, 34.0,
                              ],
            'Conductivity_S_m': [0.05, 0.052, 0.054, 0.056, 0.058, 0.06, 0.062, 0.064, 0.066, 0.068, 0.03, 0.032, 0.034,
                                 0.036, 0.038, 0.04, 0.042, 0.044, 0.046, 0.048,
                                 ],
            'Oxygen': [6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0,
                       9.5,
                       ],
            'Salinity_PSU': [33, 33.5, 34, 34.5, 35, 35.5, 36, 36.5, 37, 37.5, 32.0, 32.5, 33.0, 33.5, 34.0, 34.5, 35.0,
                             35.5, 36.0, 36.5,
                             ],
        })

    def test_add_column(self):
        self.assertNotIn("testing_col_name", self.data.columns.values)
        new_col_values = [38, 38.5, 39, 39.5, 40, 40.5,
                          41, 41.5, 42, 42.5]
        self.data = self.transformer.add_column(self.data, "testing_col_name", new_col_values)
        self.assertIn("testing_col_name", self.data.columns.values)
        npt.assert_array_equal(pd.Series(new_col_values).values, self.data["testing_col_name"].values)

    def test_create_daily_means(self):
        data_to_compute_mean = pd.DataFrame({
            'TimeStamp': [pd.to_datetime('2024-04-10 09:05:00'),
                          pd.to_datetime('2024-05-10 09:05:00'),
                          pd.to_datetime('2024-06-10 09:05:00'),
                          pd.to_datetime('2024-04-10 09:10:00'),
                          pd.to_datetime('2024-05-10 09:10:00'),
                          pd.to_datetime('2024-06-10 09:10:00'),
                          pd.to_datetime('2024-05-10 09:15:00'),
                          pd.to_datetime('2024-06-10 09:15:00'),
                          pd.to_datetime('2024-07-10 09:15:00'),
                          pd.to_datetime('2024-05-10 09:20:00'),
                          pd.to_datetime('2024-06-10 09:20:00'),
                          pd.to_datetime('2024-07-10 09:20:00')],
            'Pressure_d': [1010.0, 1010.5, 1011.0, 1011.5, 1012.0, 1012.5, 1013.0, 1013.5, 1014.0, 1014.5, 1005.0,
                           1004.5],
            'Temperature_C': [16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 25.0, 26.0]
        })
        data_real_computed = pd.DataFrame({
            'TimeStamp': ["09:05",
                          "09:10",
                          "09:15",
                          "09:20"],
            'Pressure_d': [1010.5, 1012.0, 1013.5, 1008],
            'Temperature_C': [17.0, 20.0, 23.0, 25.3333333]
        })

        data_computed = self.transformer.compute_average_per_timestamp(data_to_compute_mean, "TimeStamp")
        pdt.assert_frame_equal(data_real_computed, data_computed)

    def test_remove_values_not_in(self):
        data_2 = pd.DataFrame({
            'TimeStamp': [
                pd.to_datetime('2024-03-09 12:10:00'),
                pd.to_datetime('2024-03-09 12:15:00'),
                pd.to_datetime('2024-03-09 12:20:00'),
                pd.to_datetime('2024-03-09 12:25:00'),
                pd.to_datetime('2024-03-09 12:35:00'),
                pd.to_datetime('2024-03-09 12:40:00'),
                pd.to_datetime('2024-03-09 12:45:00')
            ],
            'Latitude_deg': [-60, -45, -30, -15, 15, 30, 45],
            'Longitude_deg': [-120, -90, -60, -30, 30, 60, 90],
            'Pressure_d': [1004.0, 1003.5, 1003.0, 1002.5, 1001.5, 1001.0, 1000.5],
            'Temperature_C': [27.0, 28.0, 29.0, 30.0, 32.0, 33.0, 34.0],
            'Conductivity_S_m': [0.034, 0.036, 0.038, 0.04, 0.044, 0.046, 0.048],
            'Oxygen': [6.0, 6.5, 7.0, 7.5, 8.5, 9.0, 9.5],
            'Salinity_PSU': [33.0, 33.5, 34.0, 34.5, 35.5, 36.0, 36.5],
        })
        result = self.transformer.remove_values_not_in(self.data, "TimeStamp", data_2).reset_index(drop=True)
        pdt.assert_frame_equal(result, data_2)

    def test_compute_day_hour(self):
        self.data = self.__define_input_compute_day_hour()

        result = self.transformer.compute_average_per_day_hour(self.data, "TimeStamp")
        real_result = self.__define_result_compute_day_hour()
        result.reset_index(drop=True, inplace=True)
        real_result.reset_index(drop=True, inplace=True)
        pdt.assert_frame_equal(result, real_result)

    def test_eliminate_outliers(self):
        self.data["Oxygen_umol_L"] = [5.0, 6.5, 1.0, 6.5, 7.0, 7.5, 8.0, 1.5, 6.0, 5.5]
        outliers = Spikes([Spikes.SpikeVariable.OXYGEN_UMOL_L] * 2, 4, [self.data["TimeStamp"][2].to_pydatetime(),
                                                             self.data["TimeStamp"][7].to_pydatetime()], [1, 1.5],
               [2, 7])

        real_final_values = pd.Series([5.0, 6.5, 6.5, 6.5, 7.0, 7.5, 8.0, 7, 6.0, 5.5], name="Oxygen_umol_L")
        df = self.transformer.interpolate_outliers(self.data, outliers, "TimeStamp")
        pdt.assert_series_equal(real_final_values, df["Oxygen_umol_L"])

    def test_sort_values(self):
        data_unordered = self.data.copy(deep=True).sample(frac=1).reset_index(drop=True)
        result = self.transformer.sort_values(data_unordered, "TimeStamp")
        pdt.assert_frame_equal(result, self.data)

    def test_filter_column_and_interpolate(self):
        wanted_result = self.data.copy(deep=True)
        self.data['Salinity_PSU'] = [32.0, 32.5, 33.0, 33.5, 34.0, 40.5, 35.0, 35.5, 36.0, 36.5]
        wanted_result['Salinity_PSU'] = [32.0, 32.5, 33.0, 33.5, 34.0, 34.5, 35.0, 35.5, 36.0, 36.5]
        pdt.assert_frame_equal(
            self.transformer.filter_column_and_interpolate(self.data, "Salinity_PSU", operator.lt, 39),
            wanted_result)

    def test_merge_columns(self):
        wanted_results = self.data.copy(deep=True)
        self.data["A"] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
        self.data["B"] = ["k", "l", "m", "n", "o", "p", "q", "r", "s", "t"]
        wanted_results['AB'] = ["a k", "b l", "c m", "d n", "e o", "f p", "g q", "h r", "i s", "j t"]
        self.data = self.transformer.merge_columns(self.data, ["A", "B"], "AB", " ")
        pdt.assert_frame_equal(wanted_results, self.data)

    def test_parse_datetime_column(self):
        df_date_str = self.data.copy(deep=True)
        df_date_str["TimeStamp"] = self.data["TimeStamp"].dt.strftime('%Y-%m-%d %H:%M:%S')
        df_date_str = self.transformer.parse_datetime_column(df_date_str, "TimeStamp")
        pdt.assert_frame_equal(df_date_str, self.data)

    def __define_input_compute_day_hour(self):
        original_latitudes = [-100,  # 21 del 8
                              -100, -90, -75, -60, -45, -30, -15, 0, 15, 30, 45,
                              -90, -75, -60, -45, -30, -15, 0, 15, 30, 45,
                              -90, -75, -60, -45,  # 24h del 9

                              -30, -15, 0, 15, 15]  #horas del 10
        dates = [
            pd.to_datetime('2024-03-08 21:00:00'),

            pd.to_datetime('2024-03-09 00:00:00'),
            pd.to_datetime('2024-03-09 01:05:00'),
            pd.to_datetime('2024-03-09 02:10:00'),
            pd.to_datetime('2024-03-09 03:15:00'),
            pd.to_datetime('2024-03-09 04:20:00'),
            pd.to_datetime('2024-03-09 05:25:00'),
            pd.to_datetime('2024-03-09 06:30:00'),
            pd.to_datetime('2024-03-09 07:35:00'),
            pd.to_datetime('2024-03-09 08:40:00'),
            pd.to_datetime('2024-03-09 09:45:00'),

            pd.to_datetime('2024-03-09 10:00:00'),
            pd.to_datetime('2024-03-09 11:00:00'),
            pd.to_datetime('2024-03-09 12:05:00'),
            pd.to_datetime('2024-03-09 13:10:00'),
            pd.to_datetime('2024-03-09 14:15:00'),
            pd.to_datetime('2024-03-09 15:20:00'),
            pd.to_datetime('2024-03-09 16:25:00'),
            pd.to_datetime('2024-03-09 17:30:00'),
            pd.to_datetime('2024-03-09 18:35:00'),
            pd.to_datetime('2024-03-09 19:40:00'),
            pd.to_datetime('2024-03-09 20:45:00'),

            pd.to_datetime('2024-03-09 21:00:00'),
            pd.to_datetime('2024-03-09 22:05:00'),
            pd.to_datetime('2024-03-09 23:10:00'),
            pd.to_datetime('2024-03-09 23:15:00'),
            pd.to_datetime('2024-03-10 05:25:00'),
            pd.to_datetime('2024-03-10 06:30:00'),
            pd.to_datetime('2024-03-10 07:35:00'),
            pd.to_datetime('2024-03-10 08:40:00'),
            pd.to_datetime('2024-03-10 09:45:00'),
        ]
        return pd.DataFrame({
            'TimeStamp': dates,
            'Latitude_deg': original_latitudes
        })

    def __define_result_compute_day_hour(self):
        dates = [
            pd.to_datetime('2024-03-08 21:00:00'),  # 0
            pd.to_datetime('2024-03-08 22:00:00'),  # 1 -2
            pd.to_datetime('2024-03-08 23:00:00'),  # 2 -2

            pd.to_datetime('2024-03-09 00:00:00'),  # 3  -2
            pd.to_datetime('2024-03-09 01:00:00'),  # 4  -2
            pd.to_datetime('2024-03-09 02:00:00'),  # 5  -2
            pd.to_datetime('2024-03-09 03:00:00'),  # 6  -2
            pd.to_datetime('2024-03-09 04:00:00'),  # 7  -2
            pd.to_datetime('2024-03-09 05:00:00'),  # 8  -2
            pd.to_datetime('2024-03-09 06:00:00'),  # 9  -2
            pd.to_datetime('2024-03-09 07:00:00'),  # 10 -2
            pd.to_datetime('2024-03-09 08:00:00'),  # 11 -2
            pd.to_datetime('2024-03-09 09:00:00'),  # 12 -2

            pd.to_datetime('2024-03-09 10:00:00'),  # 13 -2
            pd.to_datetime('2024-03-09 11:00:00'),  # 14 -2
            pd.to_datetime('2024-03-09 12:00:00'),  # 15 -2
            pd.to_datetime('2024-03-09 13:00:00'),  # 16 -2
            pd.to_datetime('2024-03-09 14:00:00'),  # 17 -2
            pd.to_datetime('2024-03-09 15:00:00'),  # 18 -2
            pd.to_datetime('2024-03-09 16:00:00'),  # 19 -2
            pd.to_datetime('2024-03-09 17:00:00'),  # 20 -2
            pd.to_datetime('2024-03-09 18:00:00'),  # 21 -2
            pd.to_datetime('2024-03-09 19:00:00'),  # 22 -2
            pd.to_datetime('2024-03-09 20:00:00'),  # 23 -2

            pd.to_datetime('2024-03-09 21:00:00'),  # 24 -2
            pd.to_datetime('2024-03-09 22:00:00'),  # 25 -2
            pd.to_datetime('2024-03-09 23:00:00'),  # 26 -2

            pd.to_datetime('2024-03-10 00:00:00'),  ##27
            pd.to_datetime('2024-03-10 01:00:00'),  ##28
            pd.to_datetime('2024-03-10 02:00:00'),  ##29
            pd.to_datetime('2024-03-10 03:00:00'),  ## 30
            pd.to_datetime('2024-03-10 04:00:00'),  ## 31

            pd.to_datetime('2024-03-10 05:00:00'),  # 32 -5
            pd.to_datetime('2024-03-10 06:00:00'),  # 33 -5
            pd.to_datetime('2024-03-10 07:00:00'),  # 34 -5
            pd.to_datetime('2024-03-10 08:00:00'),  # 35 -5
            pd.to_datetime('2024-03-10 09:00:00'),  # 36 -5
        ]
        new_latitudes = [None] * 37
        original_latitudes = [-100,  # 21 del 8
                              -100, -90, -75, -60, -45, -30, -15, 0, 15, 30, 45,
                              -90, -75, -60, -45, -30, -15, 0, 15, 30, 45,
                              -90, -75, -60, -45,  # 24h del 9
                              -30, -15, 0, 15, 15]  #horas del 10
        df = self.__define_input_compute_day_hour()
        new_latitudes[0] = original_latitudes[0]
        new_latitudes[1] = original_latitudes[23]
        new_latitudes[2] = np.mean([-60, -45])
        new_latitudes[3:27] = original_latitudes[1:25]
        new_latitudes[26] = np.mean([-60, -45])
        new_latitudes[27:32] = original_latitudes[1:6]
        new_latitudes[32:37] = original_latitudes[-5:]

        return pd.DataFrame({
            'TimeStamp': dates,
            'Latitude_deg': new_latitudes
        })
