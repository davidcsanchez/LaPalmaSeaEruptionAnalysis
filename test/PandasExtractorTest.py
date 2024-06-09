import unittest

import geopandas
import pandas as pd

from etl.extractors.CSVPandasExtractor import CSVPandasExtractor
from etl.extractors.GeoJsonGeoPandasExtractor import GeoJsonGeoPandasExtractor
import pandas.testing as pdt
import geopandas.testing as gpt

class PandasExtractorTest(unittest.TestCase):

    def setUp(self):
        self.extractor_csv_with_date = CSVPandasExtractor(["TimeStamp"],"%m/%d/%Y %I:%M %p", None)
        self.extractor_csv_without_date = CSVPandasExtractor(None, None, [0, 1, 2, 3, 4])
        self.extractor_geojson = GeoJsonGeoPandasExtractor()

    def test_csv_extractor(self):
        real_data = self.__get_csv_dataframe()
        real_data["TimeStamp"] = pd.to_datetime(real_data["TimeStamp"], format="%m/%d/%Y %I:%M %p")
        self.__assert_equal_frames(real_data, self.extractor_csv_with_date.extract("./resources/test.csv"))
        self.__assert_equal_frames(self.__get_csv_dataframe_unordered().iloc[:, :5],
                                   self.extractor_csv_without_date.extract("./resources/test.csv"))

    def test_geojson_extractor(self):
        real = self.__get_geojson_dataframe()
        extracted = self.extractor_geojson.extract("./resources/test.geojson")
        self.assertListEqual([real["geometry"]["coordinates"]],extracted.get_coordinates().values.tolist())

    def __assert_equal_frames(self, real, other):
        pdt.assert_frame_equal(real, other)

    def __get_csv_dataframe(self):
        return pd.DataFrame({
            "TimeStamp": ['11/24/2021 10:33 AM', '11/24/2021 10:42 AM', '11/24/2021 10:43 AM', '11/24/2021 10:52 AM',
                          '11/24/2021 10:53 AM'][::-1],
            "Vehicle": ["PLOCAN (SO 4089)", "PLOCAN (SO 4089)", "PLOCAN (SO 4089)", "PLOCAN (SO 4089)",
                        "PLOCAN (SO 4089)"][::-1],
            "Latitude(deg)": [28.64769, 28.64765, 28.647, 28.64698, 28.64664],
            "Longitude(deg)": [-17.99594, -17.99594, -17.995829999999994, -17.99584, -17.99594],
            "Pressure": [0.21000000000000105, 0.220000000000001, 0.25, 0.23, 0.25],
            "Temperature": [22.5985, 22.598000000000006, 22.5635, 22.5637, 22.5751],
            "Conductivity": [5.29215, 5.29212, 5.28799, 5.2879999999999985, 5.28918],
            "Oxygen_umol_L": [203.36926964128037, 203.57469485125114, 204.3751515300799, 204.29243077932102,
                       203.54426298109058],
            "Salinity (PSU)": [36.8297, 36.8299, 36.8266, 36.8266, 36.8262],
            "Payload Data": ["FD03000011360400C726080098950000", "FE0300000C360400C4260800B6950000",
                             "01040000B33404002725080018960000", "FF030000B5340400282508000C960000",
                             "01040000273504009E250800A4950000"]
        })

    def __get_csv_dataframe_unordered(self):
        return pd.DataFrame({
            "TimeStamp": ['11/24/2021 10:33 AM', '11/24/2021 10:42 AM', '11/24/2021 10:43 AM', '11/24/2021 10:52 AM',
                          '11/24/2021 10:53 AM'][::-1],
            "Vehicle": ["PLOCAN (SO 4089)", "PLOCAN (SO 4089)", "PLOCAN (SO 4089)", "PLOCAN (SO 4089)",
                        "PLOCAN (SO 4089)"],
            "Latitude(deg)": [28.64769, 28.64765, 28.647, 28.64698, 28.64664],
            "Longitude(deg)": [-17.99594, -17.99594, -17.995829999999994, -17.99584, -17.99594],
            "Pressure": [0.21000000000000105, 0.220000000000001, 0.25, 0.23, 0.25],
            "Temperature": [22.5985, 22.598000000000006, 22.5635, 22.5637, 22.5751],
            "Conductivity": [5.29215, 5.29212, 5.28799, 5.2879999999999985, 5.28918],
            "Oxygen_umol_L": [203.36926964128037, 203.57469485125114, 204.3751515300799, 204.29243077932102,
                       203.54426298109058],
            "Salinity (PSU)": [36.8297, 36.8299, 36.8266, 36.8266, 36.8262],
            "Payload Data": ["FD03000011360400C726080098950000", "FE0300000C360400C4260800B6950000",
                             "01040000B33404002725080018960000", "FF030000B5340400282508000C960000",
                             "01040000273504009E250800A4950000"]
        })

    def __get_geojson_dataframe(self):
        df = pd.DataFrame({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [-122.4194, 37.7749]  # Example coordinates for San Francisco, CA
            },
            "properties": {
                "name": "San Francisco",
                "description": "A city in California, USA"
            }
        }
        )
        return geopandas.GeoDataFrame(
            df
        )

    def __assert_equal_series(self, real, other):
        gpt.assert_geoseries_equal(real, other)
