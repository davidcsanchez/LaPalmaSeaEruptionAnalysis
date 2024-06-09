import operator
from datetime import datetime

from analyzers.PandasWaveGliderV2OceanAnalyzer import PandasWaveGliderV2OceanAnalyzer
from etl.ETL import ETL
from etl.extractors.CSVPandasExtractor import CSVPandasExtractor
from etl.extractors.GeoJsonGeoPandasExtractor import GeoJsonGeoPandasExtractor
from etl.loaders.GeoPandasMapLoader import GeoPandasMapLoader
from etl.loaders.PandasSeabedLoader import PandasSeabedLoader
from etl.loaders.PandasSpikesLoader import PandasSpikesLoader
from etl.loaders.PandasWaveGliderV2OceanLoader import PandasWaveGliderV2OceanLoader
from etl.loaders.PandasWaveGliderWeatherLoader import PandasWaveGliderWeatherLoader
from etl.transformers.PandasTransformer import PandasTransformer
from graphers.MatplotlibFigureCreator import MatplotlibFigureCreator
from graphers.MatplotlibMapChartCreator import MatplotlibMapChartCreator
from model.GeoPandasMap import GeoPandasMap
from model.ocean_devices.Seabed import Seabed
from model.Spikes import Spikes
from model.Table import Table
from model.ocean_devices.WaveGliderV2 import WaveGliderV2
from model.ocean_devices.WaveGliderV2Ocean import WaveGliderV2Ocean
from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather
from model.params.BasicPlotParams import BasicPlotParams
from model.params.ColorParams import ColorParams
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.MarkerParams import MarkerParams
from model.params.compound_params.PlotStylishParams import PlotStylishParams
from model.params.compound_params.PlotStylishSpikesParams import PlotStylishSpikesParams
from model.params.compound_params.ScatterColoredParams import ScatterColoredParams
from model.params.SpikesParams import SpikesParams
from storer.MatplotlibFigureStorer import MatplotlibFigureStorer


class AnalysisCommonTools:

    def __init__(self, data_dir: str, results_dir: str, store_date_format: str = None):
        self.data_dir = data_dir
        self.store_date_format = store_date_format
        self.results_dir = results_dir

    def get_island_map(self) -> GeoPandasMap:
        lava_map = (self.__define_map_etl()
                    .extract(self.data_dir + '/perimetro_dron_211215.geojson')
                    .load())
        full_map = (self.__define_map_etl()
                    .extract(self.data_dir + '/limite_insular.geojson')
                    .concat_data(lava_map)
                    .add_column("label", ["La Palma", "Coladas de lava"])
                    .load())
        return full_map

    def __define_map_etl(self) -> ETL:
        return ETL(GeoJsonGeoPandasExtractor(), PandasTransformer(), GeoPandasMapLoader())

    def define_etl_glider(self, parse_dates: list[str], date_format: str, relevant_cols_idx: list[int],
                          delimiter: str = ",") -> ETL:
        return ETL(CSVPandasExtractor(parse_dates, date_format, relevant_cols_idx, delimiter), PandasTransformer(),
                   PandasWaveGliderV2OceanLoader())

    def define_etl_weather(self, parse_dates: list[str] | None, date_format: str | None, relevant_col_idx: list[int]):
        return ETL(CSVPandasExtractor(parse_dates, date_format, relevant_col_idx), PandasTransformer(),
                   PandasWaveGliderWeatherLoader())

    def define_seabed_etl(self, parse_dates: list[str] | None, date_format: str | None, relevant_cols_idx: list[int],
                          delimiter: str = ","):
        return ETL(CSVPandasExtractor(parse_dates, date_format, relevant_cols_idx, delimiter=delimiter),
                   PandasTransformer(), PandasSeabedLoader())

    def define_etl_spikes(self, parse_dates: list[str], date_format: str, relevant_cols_idx: list[int],
                          delimiter: str = ",", index_col: list[int] = False) -> ETL:
        return ETL(CSVPandasExtractor(parse_dates, date_format, relevant_cols_idx, delimiter, index_col),
                   PandasTransformer(),
                   PandasSpikesLoader())

    def create_time_series_with_spikes_plot(self, wave_glider: WaveGliderV2Ocean,
                                            analyzer: PandasWaveGliderV2OceanAnalyzer,
                                            title: str, filename: str) -> Table:
        outliers_table = self.draw_time_series_with_spikes(wave_glider, title, analyzer)
        MatplotlibFigureStorer().store(self.results_dir + filename)
        return outliers_table

    def draw_time_series_with_spikes(self, glider: WaveGliderV2Ocean, title: str,
                                     analyzer: PandasWaveGliderV2OceanAnalyzer) -> Table:
        salinity_outliers = analyzer.analyze_outliers_salinity(glider)
        oxygen_outliers = analyzer.analyze_outliers_oxygen(glider)
        temperature_plot_params, conductivity_plot_params, salinity_plot_params, oxygen_plot_params = (
            self.__define_wave_glider_data_plot_params(glider, salinity_outliers, oxygen_outliers))
        MatplotlibFigureCreator(4, 1, (15, 10)).create_timeseries_with_outliers(
            [temperature_plot_params, conductivity_plot_params],
            [salinity_plot_params, oxygen_plot_params],
            title,
            glider.timestamp)
        return salinity_outliers.to_table().concat_equal_tables(oxygen_outliers.to_table())

    def create_weather_mean_daily_plot(self, weather: WaveGliderV2Weather, title: str, filename: str) -> None:
        visualizer = MatplotlibFigureCreator(1, 1, (14, 7))
        visualizer.set_three_plotters_one_figure()
        wind_plot_params, temperature_plot_params, gust_wind_plot_params = self.define_daily_means_plot_params(
            weather)
        visualizer.create_daily_means([temperature_plot_params, wind_plot_params],
                                      [gust_wind_plot_params],
                                      title,
                                      weather.timestamp)
        MatplotlibFigureStorer().store(self.results_dir + filename)

    def define_data_colored_map_params(self, wave_glider: WaveGliderV2Ocean,
                                       area_to_plot: tuple[float, float, float, float]) \
            -> list[ScatterColoredParams]:
        return [
            ScatterColoredParams(
                BasicPlotParams(wave_glider.longitude_deg, wave_glider.latitude_deg, "Temperatura"),
                ColorParams(wave_glider.temperature_c, "viridis", "Temperatura Cº", "white"),
                LimitedPlotArea(*area_to_plot)),
            ScatterColoredParams(
                BasicPlotParams(wave_glider.longitude_deg, wave_glider.latitude_deg, "Salinidad"),
                ColorParams(wave_glider.salinity_psu, "viridis", "Salinidad PSU", "white"),
                LimitedPlotArea(*area_to_plot)),
            ScatterColoredParams(
                BasicPlotParams(wave_glider.longitude_deg, wave_glider.latitude_deg, "Oxígeno"),
                ColorParams(wave_glider.oxygen, "viridis", "Oxígeno", "white"),
                LimitedPlotArea(*area_to_plot)),
            ScatterColoredParams(
                BasicPlotParams(wave_glider.longitude_deg, wave_glider.latitude_deg, "Conductividad"),
                ColorParams(wave_glider.conductivity_s_m, "viridis", "Conductividad S/m", "white"),
                LimitedPlotArea(*area_to_plot))
        ]

    def define_daily_means_plot_params(self, weather: WaveGliderV2Weather) -> \
            tuple[PlotStylishParams, PlotStylishParams, PlotStylishParams]:
        temperature_plot_params = PlotStylishParams(
            BasicPlotParams(weather.index, weather.temperature_c, ""),
            MarkerParams("coral", "Temperatura", "-", 1),
            LimitedPlotArea(min(weather.index), max(weather.index), self.calculate_min_lim(weather.temperature_c),
                            self.calculate_max_lim(weather.temperature_c)))
        wind_plot_params = PlotStylishParams(
            BasicPlotParams(weather.index, weather.wind_speed_kt, ""),
            MarkerParams("darkolivegreen", "Velocidad viento", "--", 1),
            LimitedPlotArea(min(weather.index), max(weather.index), self.calculate_min_lim(weather.wind_speed_kt),
                            self.calculate_max_lim(weather.wind_speed_kt)))
        gust_wind_plot_params = PlotStylishParams(
            BasicPlotParams(weather.index, weather.wind_gust_speed_kt, ""),
            MarkerParams("indigo", "Ráfagas de viento", "o", 10),
            LimitedPlotArea(min(weather.index), max(weather.index), self.calculate_min_lim(weather.wind_gust_speed_kt),
                            self.calculate_max_lim(weather.wind_gust_speed_kt)))
        return wind_plot_params, temperature_plot_params, gust_wind_plot_params

    def define_weather_plot_params(self, weather: WaveGliderV2Weather) -> \
            tuple[PlotStylishParams, PlotStylishParams, PlotStylishParams]:
        temperature_plot_params = PlotStylishParams(
            BasicPlotParams(weather.index, weather.temperature_c, "Temperatura"),
            MarkerParams("coral", "Temperatura", "-", 1),
            LimitedPlotArea(min(weather.index), max(weather.index), self.calculate_min_lim(weather.temperature_c),
                            self.calculate_max_lim(weather.temperature_c)))
        wind_plot_params = PlotStylishParams(
            BasicPlotParams(weather.index, weather.wind_speed_kt, "Velocidad viento"),
            MarkerParams("darkolivegreen", "Velocidad viento", "--", 1),
            LimitedPlotArea(min(weather.index), max(weather.index), self.calculate_min_lim(weather.wind_speed_kt),
                            self.calculate_max_lim(weather.wind_speed_kt)))
        gust_wind_plot_params = PlotStylishParams(
            BasicPlotParams(weather.index, weather.wind_gust_speed_kt, "Velocidad de ráfagas de viento"),
            MarkerParams("indigo", "Ráfagas de viento", "o", 10),
            LimitedPlotArea(min(weather.index), max(weather.index), self.calculate_min_lim(weather.wind_gust_speed_kt),
                            self.calculate_max_lim(weather.wind_gust_speed_kt)))
        return wind_plot_params, temperature_plot_params, gust_wind_plot_params

    def calculate_min_lim(self, value_list: list[float]) -> float:
        return min(value_list) - 0.05 * min(value_list)

    def calculate_max_lim(self, value_list: list[float]) -> float:
        return max(value_list) + 0.05 * max(value_list)

    def calculate_min_lim_salinity(self, value_list: list[float]) -> float:
        return min(value_list) - 0.005 * min(value_list)

    def calculate_max_lim_salinity(self, value_list: list[float]) -> float:
        return max(value_list) + 0.005 * max(value_list)

    def create_weather_plot(self, weather: WaveGliderV2Weather, title: str, filename) -> None:
        visualizer = MatplotlibFigureCreator(3, 1, (14, 8))
        wind_plot_params, temperature_plot_params, gust_wind_plot_params = self.define_weather_plot_params(weather)
        visualizer.create_timeseries([temperature_plot_params, wind_plot_params],
                                     [gust_wind_plot_params], title,
                                     weather.timestamp)
        MatplotlibFigureStorer().store(self.results_dir + filename)

    def create_travel_map(self, map: GeoPandasMap, wave_glider_22: WaveGliderV2Ocean,
                          area_to_plot: tuple[float, float, float, float]) -> None:
        plots = self.__define_travel_params(wave_glider_22, area_to_plot)
        visualizer = MatplotlibMapChartCreator(2, 2, (20, 20))
        visualizer.add_map_to_plots(map, "label", ["orangered", "darkgreen"])
        visualizer.create_map_with_data_directions(plots, "Recorrido de la misión de 2022")
        MatplotlibFigureStorer().store(self.results_dir + "/recorrido_por_partes_glider_22.jpg")

    def __define_travel_params(self, glider: WaveGliderV2Ocean, area_to_plot: tuple[float, float, float, float]) \
            -> list[ScatterColoredParams]:
        return [
            self.__create_divided_map_plot_param(glider, area_to_plot, "Tiempo en milisengundos desde 1/1/1970",
                                                 self.__datetime_list_to_milliseconds(glider.timestamp), 0, 0.25),
            self.__create_divided_map_plot_param(glider, area_to_plot, "Tiempo en milisengundos desde 1/1/1970",
                                                 self.__datetime_list_to_milliseconds(glider.timestamp), 0.25, 0.5),
            self.__create_divided_map_plot_param(glider, area_to_plot, "Tiempo en milisengundos desde 1/1/1970",
                                                 self.__datetime_list_to_milliseconds(glider.timestamp), 0.5, 0.75),
            self.__create_divided_map_plot_param(glider, area_to_plot, "Tiempo en milisengundos desde 1/1/1970",
                                                 self.__datetime_list_to_milliseconds(glider.timestamp), 0.75, 1)
        ]

    def __create_divided_map_plot_param(self, wave_glider: WaveGliderV2Ocean,
                                        area_to_plot: tuple[float, float, float, float],
                                        colored_label: str, values_to_plot: list[float], start_percent: float,
                                        end_percent: float) -> ScatterColoredParams:
        start_idx = round(len(values_to_plot) * start_percent)
        end_idx = round(len(values_to_plot) * end_percent)
        return ScatterColoredParams(
            BasicPlotParams(wave_glider.longitude_deg[start_idx:end_idx], wave_glider.latitude_deg[start_idx:end_idx],
                            "Desde el " + str(wave_glider.timestamp[start_idx].date()) +
                            " hasta el " + str(wave_glider.timestamp[end_idx - 1].date())),
            ColorParams(values_to_plot[start_idx:end_idx], "viridis", colored_label),
            LimitedPlotArea(*area_to_plot)
        )

    def __datetime_list_to_milliseconds(self, datetime_list: list[datetime]) -> list[float]:
        return list(map(lambda dt: dt.timestamp() * 1000, datetime_list))

    def __define_wave_glider_data_plot_params(self, cleaned_22_data: WaveGliderV2Ocean, salinity_outliers: Spikes,
                                              oxygen_outliers: Spikes) \
            -> tuple[PlotStylishParams, PlotStylishParams, PlotStylishSpikesParams, PlotStylishSpikesParams]:
        temperature_plot_params = PlotStylishParams(
            BasicPlotParams(cleaned_22_data.index, cleaned_22_data.temperature_c, "Temperatura"),
            MarkerParams("coral", "Temperatura", "-", 1),
            LimitedPlotArea(min(cleaned_22_data.index),max(cleaned_22_data.index),
                            self.calculate_min_lim(cleaned_22_data.temperature_c),
                            self.calculate_max_lim(cleaned_22_data.temperature_c)))
        conductivity_plot_params = PlotStylishParams(
            BasicPlotParams(cleaned_22_data.index, cleaned_22_data.conductivity_s_m, "Conductividad"),
            MarkerParams("darkolivegreen", "Conductividad", "--", 1),
            LimitedPlotArea(min(cleaned_22_data.index),max(cleaned_22_data.index),
                            self.calculate_min_lim(cleaned_22_data.conductivity_s_m),
                            self.calculate_max_lim(cleaned_22_data.conductivity_s_m)))
        salinity_plot_params = PlotStylishSpikesParams(
            BasicPlotParams(cleaned_22_data.index, cleaned_22_data.salinity_psu, "Salinidad"),
            MarkerParams("indigo", "Salinidad PSU", "o", 10),
            LimitedPlotArea(min(cleaned_22_data.index), max(cleaned_22_data.index),
                            self.calculate_min_lim_salinity(cleaned_22_data.salinity_psu),
                            self.calculate_max_lim_salinity(cleaned_22_data.salinity_psu)),
            SpikesParams(salinity_outliers.indexes,
                         salinity_outliers.values,
                               "red")
        )
        oxygen_plot_params = PlotStylishSpikesParams(
            BasicPlotParams(cleaned_22_data.index, cleaned_22_data.oxygen, "Oxígeno"),
            MarkerParams("goldenrod", "Oxígeno", "o", 10),
            LimitedPlotArea(min(cleaned_22_data.index),max(cleaned_22_data.index),
                            self.calculate_min_lim(cleaned_22_data.oxygen),
                            self.calculate_max_lim(cleaned_22_data.oxygen)),
            SpikesParams(oxygen_outliers.indexes,
                         oxygen_outliers.values,
                               "black")
        )
        return temperature_plot_params, conductivity_plot_params, salinity_plot_params, oxygen_plot_params

    def get_column_from_table(self, table: Table, label: str) -> list:
        for column in table.columns:
            if column.label == label:
                return column.values

    def get_spikes(self, table_filename: str) -> Spikes:
        return (self.define_etl_spikes(["TimeStamp"],  "%d/%m/%Y %H:%M",
                                       [0, 1, 2, 3, 4], ",", [0])
                .extract(table_filename)
                .load())

    def define_wave_glider_ocean_variable_renames(self) -> dict[str, str]:
        return {"Temperature": "Temperature_C", "Conductivity": "Conductivity_S_m",
                "Salinity (PSU)": "Salinity_PSU", "Oxygen": "Oxygen_umol_L",
                "Pressure": "Pressure_d", "Latitude(deg)": "Latitude_deg",
                "Longitude(deg)": "Longitude_deg"}

    def define_wave_glider_weather_variable_renames(self) -> dict[str, str]:
        return {"Temperature(degC)": "Temperature_C", "Wind Speed(kt)": "Wind_speed_kt","Latitude" : "Latitude_deg",
                "Longitude" : "Longitude_deg", "Pressure(mb)" : "Pressure_d",
                "Wind Gust Speed(kt)": "Wind_gust_speed_kt", 'Wind Direction': "Wind_direction"}

    def define_variable_renames_to_spanish(self) -> dict[str, str]:
        return {"Temperature_C": "Temperatura Cº", "Conductivity_S_m": "Conductividad S/m",
                "Salinity_PSU": "Salinidad PSU", "Oxygen_umol_L": "Oxígeno umol/L", "TimeStamp" : "TimeStamp",
                "Pressure_d": "Presión en decibares", "Latitude_deg": "Latitud en grados",
                "Longitude_deg": "Longitud en grados", "Wind_speed_kt": "Velocidad del viento en nudos",
                "Wind_direction": "Dirección del viento", "Wind_gust_speed_kt" : "Velocidad de ráfagas de viento"}

    def get_data(self) -> tuple[
        WaveGliderV2Ocean, WaveGliderV2Weather, WaveGliderV2, WaveGliderV2Ocean, WaveGliderV2Weather,
        WaveGliderV2, WaveGliderV2Ocean, WaveGliderV2, Seabed, Seabed]:
        cols_renames_ocean, cols_renames_weather, start_drift_21, start_drift_22 = (
            self.define_ocean_preprocess_variables())
        ocean_21, weather_21, glider_21 = self.get_glider_21_data(cols_renames_ocean, cols_renames_weather,
                                                                  start_drift_21)
        ocean_22, glider_22, drifted_22, glider_drifted_22, weather_22 = self.get_glider_22_data(cols_renames_ocean,
                                                                                                 cols_renames_weather,
                                                                                                 start_drift_22)
        return (ocean_21, weather_21, glider_21, ocean_22, weather_22, glider_22, drifted_22, glider_drifted_22,
                (self.get_seabed_23_data()),
                (self.get_seabed_24_data()))

    def define_ocean_preprocess_variables(self) -> tuple[dict[str, str], dict[str, str], str, str]:
        return (self.define_wave_glider_ocean_variable_renames(),
                self.define_wave_glider_weather_variable_renames(),
                '2021-11-09 15:30:00', '2022-03-09 15:30:00')

    def get_glider_21_data(self, cols_renames_glider: dict[str, str], cols_renames_weather: dict[str, str],
                           glider_drift_start_date: str) -> tuple[WaveGliderV2Ocean, WaveGliderV2Weather, WaveGliderV2]:
        spikes_21 = self.get_spikes(self.results_dir + "/../exploratory/glider21/outliers_wg2_21.csv")
        etl_ocean_glider = self.define_etl_glider(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                                  [0, 2, 3, 4, 5, 6, 7, 8])
        ocean_21 = ((etl_ocean_glider.extract(self.data_dir + "/WG_211009_211124/MERGED_CTD_withOxygenCalc.csv"))
                    .rename_columns(cols_renames_glider)
                    .filter_column("TimeStamp", operator.lt, glider_drift_start_date)
                    .interpolate_outliers(spikes_21, "TimeStamp")
                    .sort_values("TimeStamp")
                    .load())
        weather_etl = self.define_etl_weather(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                              [0, 3, 4, 5, 6, 8, 9])
        weather_21 = (weather_etl
                      .extract(self.data_dir + "/WG_211009_211124/MERGED_WEATHER.csv", )
                      .rename_columns(cols_renames_weather).filter_column("TimeStamp", operator.lt,
                                                                          glider_drift_start_date)
                      .sort_values("TimeStamp")
                      .load())
        return ocean_21, weather_21, self.create_glider_obj(etl_ocean_glider, weather_etl)

    def get_glider_22_data(self, cols_rename_glider: dict[str, str], cols_rename_weather: dict[str, str],
                           glider_drift_start_date: str) \
            -> tuple[WaveGliderV2Ocean, WaveGliderV2, WaveGliderV2Ocean, WaveGliderV2, WaveGliderV2Weather]:
        spikes_22 = self.get_spikes(self.results_dir + "/../exploratory/glider22/outliers_wg2_22.csv")
        spikes_22_drifted = self.get_spikes(self.results_dir + "/../exploratory/glider22/outliers_wg2_desviado_22.csv")
        etl_ocean_22 = self.define_etl_glider(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                              [0, 2, 3, 4, 5, 6, 7, 8])
        etl_drifted_22 = self.define_etl_glider(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                                [0, 2, 3, 4, 5, 6, 7, 8])
        weather_etl = self.define_etl_weather(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                              [0, 3, 4, 5, 6, 8, 9])
        weather_etl_drifted = self.define_etl_weather(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                                      [0, 3, 4, 5, 6, 8, 9])
        drifted_22, ocean_22 = self.get_ocean_data_22(cols_rename_glider, etl_drifted_22, etl_ocean_22,
                                                      glider_drift_start_date, spikes_22, spikes_22_drifted)
        weather_22, weather_drifted_22 = self.get_weather_data_22(cols_rename_weather, glider_drift_start_date,
                                                                  weather_etl,
                                                                  weather_etl_drifted)
        return (ocean_22, self.create_glider_obj(etl_ocean_22, weather_etl),
                drifted_22, self.create_glider_obj(etl_drifted_22, weather_etl_drifted), weather_22)

    def create_glider_obj(self, etl_ocean: ETL, etl_weather: ETL) -> WaveGliderV2:
        ocean_hour_mean = (etl_ocean
                           .compute_average_per_day_hour("TimeStamp")
                           .remove_values_not_in("TimeStamp",
                                                 etl_weather.compute_average_per_day_hour("TimeStamp"))
                           .sort_values("TimeStamp")
                           .load())
        weather_hour_mean = (etl_weather.remove_values_not_in("TimeStamp", etl_ocean)
                             .sort_values("TimeStamp")
                             .load())
        return WaveGliderV2(ocean_hour_mean, weather_hour_mean)

    def get_ocean_data_22(self, cols_rename_glider, etl_drifted_22, etl_ocean_22, glider_drift_start_date,
                          spikes_22: Spikes, spikes_22_drifted: Spikes):
        ocean_22 = (etl_ocean_22
                    .extract(self.data_dir + "/WG_220202_220318/MERGED_CTD_withOxygenCalc.csv")
                    .rename_columns(cols_rename_glider)
                    .filter_column("TimeStamp", operator.lt, glider_drift_start_date)
                    .filter_column("Pressure_d", operator.gt, 0)
                    .interpolate_outliers(spikes_22, "TimeStamp")
                    .sort_values("TimeStamp")
                    .load())
        drifted_22 = (etl_drifted_22
                      .extract(self.data_dir + "/WG_220202_220318/MERGED_CTD_withOxygenCalc.csv")
                      .rename_columns(cols_rename_glider)
                      .filter_column("TimeStamp", operator.gt, glider_drift_start_date)
                      .filter_column("Pressure_d", operator.gt, 0)
                      .interpolate_outliers(spikes_22_drifted, "TimeStamp")
                      .filter_column_and_interpolate("Conductivity_S_m", operator.gt, 4.7)
                      .sort_values("TimeStamp")
                      .load())
        return drifted_22, ocean_22

    def get_weather_data_22(self, cols_rename_weather: dict[str, str], glider_drift_start_date: str,
                            weather_etl: ETL, weather_etl_drifted: ETL):
        weather_22 = (weather_etl.extract(self.data_dir + "/WG_220202_220318/MERGED_WEATHER.csv", )
                      .rename_columns(cols_rename_weather)
                      .filter_column("TimeStamp", operator.lt, glider_drift_start_date)
                      .sort_values("TimeStamp")
                      .load())
        weather_drifted_22 = (weather_etl_drifted.extract(self.data_dir + "/WG_220202_220318/MERGED_WEATHER.csv")
                              .rename_columns(cols_rename_weather)
                              .filter_column("TimeStamp", operator.gt, glider_drift_start_date)
                              .sort_values("TimeStamp")
                              .load())
        return weather_22, weather_drifted_22

    def get_seabed_23_data(self) -> Seabed:
        spikes = self.get_spikes(self.results_dir + "/../exploratory/seabed/outliers_fondeo_23.csv")
        return (self.define_seabed_etl(["Time"], "%d/%m/%Y %H:%M",
                                       [1, 2, 3, 4])
                .extract(self.data_dir + "/Fondeo_230601_230614/sbe37sm-rs232_03714295_2023_06_16.csv")
                .rename_columns({"Time": "TimeStamp"})
                .interpolate_outliers(spikes, "TimeStamp")
                .sort_values("TimeStamp")
                .load())

    def get_seabed_24_data(self) -> Seabed:
        spikes = self.get_spikes(self.results_dir + "/../exploratory/seabed/outliers_fondeo_23.csv")
        return (self.define_seabed_etl(None, None,
                                       [0, 1, 2, 3, 4, 5, 6], r"\s+")
                .extract(self.data_dir + "/Fondeo_24/sbe37sm-rs232_03714294_2024_04_10.asc")
                .merge_columns(["Day", "Month", "Year", "Time"], "TimeStamp", " ")
                .parse_datetime_column("TimeStamp")
                .filter_column("Conductivity_S_m", operator=operator.ge, value=1)
                .interpolate_outliers(spikes, "TimeStamp")
                .sort_values("TimeStamp")
                .load())
