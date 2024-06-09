import operator

from AnalysisCommonTools import AnalysisCommonTools
from analyzers.PandasWaveGliderV2OceanAnalyzer import PandasWaveGliderV2OceanAnalyzer
from analyzers.PandasWaveGliderV2WeatherAnalyzer import PandasWaveGliderV2WeatherAnalyzer
from etl.ETL import ETL
from etl.extractors.CSVPandasExtractor import CSVPandasExtractor
from etl.loaders.PandasWaveGliderWeatherLoader import PandasWaveGliderWeatherLoader
from etl.transformers.PandasTransformer import PandasTransformer
from graphers.MatplotlibMapChartCreator import MatplotlibMapChartCreator
from model.GeoPandasMap import GeoPandasMap
from model.Table import Table
from model.ocean_devices.WaveGliderV2Ocean import WaveGliderV2Ocean
from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather
from model.params.BasicPlotParams import BasicPlotParams
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.compound_params.LimitedPlotParams import LimitedPlotParams
from storer.CsvPandasStorer import CsvPandasStorer
from storer.MatplotlibFigureStorer import MatplotlibFigureStorer

RESULTS_DIRECTORY = "./results/exploratory/glider21"
STORE_DATE_FORMAT = "%d/%m/%Y %H:%M"
DATA_DIR = "./data"
common_tools = AnalysisCommonTools(DATA_DIR, RESULTS_DIRECTORY, STORE_DATE_FORMAT)


def main():
    full_map = common_tools.get_island_map()
    wave_glider_21_cleaned, wave_glider_21_original, glider_drifted_21 = get_ctd_21_data(
        *define_21_preprocess_variables())
    glider_22_cleaned, drifted_22 = get_ctd_clean_22_data(*define_22_preprocess_variables())
    weather, daily = get_weather_data(*define_weather_preprocess_variables())
    create_first_map(full_map, wave_glider_21_cleaned, wave_glider_21_original)
    outliers_table = (common_tools
                      .create_time_series_with_spikes_plot(wave_glider_21_cleaned,
                                                           PandasWaveGliderV2OceanAnalyzer(wave_glider_21_cleaned,
                                                                                           glider_22_cleaned,
                                                                                           drifted_22),
                                                           "Visualización inicial de los datos de la misión 2021",
                                                           "/datos_glider_21.jpg"))
    store_analyzed_data(wave_glider_21_cleaned, glider_drifted_21, weather, outliers_table)
    create_map_with_all_data(full_map, wave_glider_21_cleaned, (-18.1, -17.9, 28.45, 28.70))
    common_tools.create_travel_map(full_map, wave_glider_21_cleaned, (-18.1, -17.9, 28.46, 28.685))
    common_tools.create_weather_plot(weather, "Visualización del clima de la misión de 2021",
                                          "/weather_data_21.jpg")
    common_tools.create_weather_mean_daily_plot(daily,
                                                     "Visualización de medias por hora en datos del clima de la misión 2021",
                                                     "/visualización_de_media_diaria_clima_21.jpg")


def create_first_map(full_map: GeoPandasMap, wave_glider_21_cleaned: WaveGliderV2Ocean,
                     wave_glider_21_original: WaveGliderV2Ocean) -> None:
    visualizer = MatplotlibMapChartCreator(1, 2, (15, 10))
    visualizer.add_map_to_plots(full_map, "label", ["orangered", "darkgreen"])
    visualizer.create_map(define_first_map_params(wave_glider_21_cleaned, wave_glider_21_original),
                          "Limpieza de datos del recorrido de la misión 2021")
    MatplotlibFigureStorer().store(RESULTS_DIRECTORY + "/recorrido_glider_2021.jpg")


def create_map_with_all_data(full_map: GeoPandasMap, wave_glider_21_cleaned: WaveGliderV2Ocean,
                             area_to_plot: tuple[float, float, float, float]) -> None:
    plot_params = common_tools.define_data_colored_map_params(wave_glider_21_cleaned, area_to_plot)
    visualizer = MatplotlibMapChartCreator(2, 2, (20, 20), )
    visualizer.add_map_to_plots(full_map, "label", ["orangered", "darkgreen"])
    visualizer.create_map_with_data(plot_params,
                                    "Datos en el recorrido de la misión de 2021 \n para cada una las variables consideradas")
    MatplotlibFigureStorer().store(RESULTS_DIRECTORY + "/recorrido_con_datos_glider_21.jpg")


def get_ctd_21_data(cols_renames: dict[str, str], glider_drift_start_date: str, glider_drift_end_date: str) \
        -> tuple[WaveGliderV2Ocean, WaveGliderV2Ocean, WaveGliderV2Ocean]:
    glider_21 = (common_tools.define_etl_glider(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                                [0, 2, 3, 4, 5, 6, 7, 8])
                 .extract(DATA_DIR + "/WG_211009_211124/MERGED_CTD_withOxygenCalc.csv")
                 .rename_columns(cols_renames)
                 .sort_values("TimeStamp")
                 .load())
    cleaned_21_data = (common_tools.define_etl_glider(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                                      [0, 2, 3, 4, 5, 6, 7, 8])
                       .extract(DATA_DIR + "/WG_211009_211124/MERGED_CTD_withOxygenCalc.csv")
                       .rename_columns(cols_renames)
                       .filter_column("TimeStamp", operator.lt, glider_drift_start_date)
                       .sort_values("TimeStamp")
                       .load())
    drifted_21_data = (common_tools.define_etl_glider(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                                      [0, 2, 3, 4, 5, 6, 7, 8])
                       .extract(DATA_DIR + "/WG_211009_211124/MERGED_CTD_withOxygenCalc.csv")
                       .rename_columns(cols_renames)
                       .filter_column("TimeStamp", operator.gt, glider_drift_start_date)
                       .filter_column("TimeStamp", operator.lt, glider_drift_end_date)
                       .sort_values("TimeStamp")
                       .load())
    return cleaned_21_data, glider_21, drifted_21_data


def store_analyzed_data(wave_glider_21: WaveGliderV2Ocean, drifted_21: WaveGliderV2Ocean,
                        weather_21: WaveGliderV2Weather, outliers: Table) -> None:
    glider_analyzer = PandasWaveGliderV2OceanAnalyzer()
    weather_analyzer = PandasWaveGliderV2WeatherAnalyzer()
    spanish_variable_renames = common_tools.define_variable_renames_to_spanish()
    (CsvPandasStorer(format_dict=spanish_variable_renames)
     .store(glider_analyzer.describe(wave_glider_21),
            RESULTS_DIRECTORY + "/datos_glider_21.csv", STORE_DATE_FORMAT, True)
     .store(glider_analyzer.analyze_null_and_unique_values(wave_glider_21),
            RESULTS_DIRECTORY + "/conteo_glider_21.csv", STORE_DATE_FORMAT, True, True, ["indexes"])
     .store(glider_analyzer.data_continuity(wave_glider_21, 100),
            RESULTS_DIRECTORY + "/continuidad_fechas_glider_21.csv", STORE_DATE_FORMAT, False)
     .store(glider_analyzer.describe(drifted_21),
            RESULTS_DIRECTORY + "/datos_desvío_21.csv", STORE_DATE_FORMAT, True)
     .store(outliers, RESULTS_DIRECTORY + "/outliers_wg2_21.csv", STORE_DATE_FORMAT, True, )
     .store(weather_analyzer.describe(weather_21),
            RESULTS_DIRECTORY + "/datos_clima_21.csv", STORE_DATE_FORMAT, True)
     .store(weather_analyzer.analyze_null_and_unique_values(weather_21),
            RESULTS_DIRECTORY + "/conteo_clima_21.csv", STORE_DATE_FORMAT, True, True, ["indexes"])
     .store(weather_analyzer.data_continuity(weather_21, 100),
            RESULTS_DIRECTORY + "/continuidad_fechas_clima_21.csv", STORE_DATE_FORMAT, False))


def get_weather_data(col_renames: dict[str, str], glider_out_route_date: str) -> \
        tuple[WaveGliderV2Weather, WaveGliderV2Weather]:
    weather = (ETL(CSVPandasExtractor(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                      [0, 3, 4, 5, 6, 8, 9]), PandasTransformer(), PandasWaveGliderWeatherLoader())
               .extract(DATA_DIR + "/WG_211009_211124/MERGED_WEATHER.csv", )
               .rename_columns(col_renames).filter_column("TimeStamp", operator.lt, glider_out_route_date)
               .sort_values("TimeStamp")
               .load())
    daily_means = (ETL(CSVPandasExtractor(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                          [0, 3, 4, 5, 6, 8, 9]), PandasTransformer(), PandasWaveGliderWeatherLoader())
                   .extract(DATA_DIR + "/WG_211009_211124/MERGED_WEATHER.csv")
                   .rename_columns(col_renames).filter_column("TimeStamp", operator.lt, glider_out_route_date)
                   .compute_average_per_timestamp("TimeStamp")
                   .sort_values("TimeStamp")
                   .load())
    return weather, daily_means


def get_column_from_table(table: Table, label: str) -> list:
    for column in table.columns:
        if column.label == label:
            return column.values


def define_21_preprocess_variables() -> tuple[dict[str, str], str, str]:
    return common_tools.define_wave_glider_ocean_variable_renames(), '2021-11-09 15:30:00', '2021-11-21 19:30:00'


def define_weather_preprocess_variables() -> tuple[dict[str, str], str]:
    return common_tools.define_wave_glider_weather_variable_renames(), '2021-11-09 15:30:00'


def define_first_map_params(wave_glider_cleaned: WaveGliderV2Ocean, wave_glider_original: WaveGliderV2Ocean) -> \
        list[LimitedPlotParams]:
    return [LimitedPlotParams(BasicPlotParams(wave_glider_original.longitude_deg, wave_glider_original.latitude_deg,
                                              'Datos antes de preprocesar'),
                              LimitedPlotArea(-18.3, -17.85, 27.9, 28.75)),
            LimitedPlotParams(
                BasicPlotParams(wave_glider_cleaned.longitude_deg, wave_glider_cleaned.latitude_deg,
                                "Datos después del preprocesado"), LimitedPlotArea(-18.1, -17.85, 28.45, 28.70))]


def get_ctd_clean_22_data(cols_renames: dict[str, str], drifted_glider_date: str) \
        -> tuple[WaveGliderV2Ocean, WaveGliderV2Ocean]:
    glider_22_cleaned = (common_tools.define_etl_glider(["TimeStamp"], '%m/%d/%Y %I:%M %p',
                                                        [0, 2, 3, 4, 5, 6, 7, 8])
                         .extract(DATA_DIR + "/WG_220202_220318/MERGED_CTD_withOxygenCalc.csv")
                         .rename_columns(cols_renames)
                         .filter_column("TimeStamp", operator.lt, drifted_glider_date)
                         .filter_column("Pressure_d", operator.gt, 0)
                         .sort_values("TimeStamp")
                         .load())
    drifted_22 = (common_tools.define_etl_glider(["TimeStamp"], '%m/%d/%Y %I:%M %p',
                                                 [0, 2, 3, 4, 5, 6, 7, 8])
                  .extract(DATA_DIR + "/WG_220202_220318/MERGED_CTD_withOxygenCalc.csv")
                  .rename_columns(cols_renames)
                  .filter_column("TimeStamp", operator.gt, drifted_glider_date)
                  .filter_column("Pressure_d", operator.gt, 0)
                  .sort_values("TimeStamp")
                  .load())
    return glider_22_cleaned, drifted_22


def define_22_preprocess_variables() -> tuple[dict[str, str], str]:
    return common_tools.define_wave_glider_ocean_variable_renames(), '2022-03-09 15:30:00'


main()
