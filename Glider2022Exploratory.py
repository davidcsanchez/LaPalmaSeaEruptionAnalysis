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

RESULTS_DIRECTORY = "./results/exploratory/glider22"
STORE_DATE_FORMAT = "%d/%m/%Y %H:%M"
DATA_DIR = "data"
common_analysis_tools = AnalysisCommonTools(DATA_DIR, RESULTS_DIRECTORY, STORE_DATE_FORMAT)


def main():
    full_map = common_analysis_tools.get_island_map()
    glider_22_cleaned, glider_22_original, drifted_22 = get_ctd_22_data(*define_22_preprocess_variables())
    wave_glider_21_cleaned = get_ctd_clean_21_data(*define_21_preprocess_variables_for_clean_data())
    weather_22, daily_22, weather_drifted_22, daily_22_drifted = get_weather_data(
        *define_weather_preprocess_variables())
    create_first_map(full_map, glider_22_cleaned, glider_22_original)
    analyzer = PandasWaveGliderV2OceanAnalyzer(glider_22_cleaned, drifted_22, wave_glider_21_cleaned)
    outliers_22_table = common_analysis_tools.create_time_series_with_spikes_plot(glider_22_cleaned, analyzer,
                                                                              "Visualización inicial de los datos de la misión 2022 cercanos al evento",
                                                                              "/datos_glider_22.jpg")
    outliers_drifted_table = common_analysis_tools.create_time_series_with_spikes_plot(drifted_22, analyzer,
                                                                                   "Visualización inicial de los datos de la misión 2022 lejanos al evento",
                                                                                   "/datos_glider_desviado_22.jpg")

    analyze_data(glider_22_cleaned, weather_22, drifted_22, weather_drifted_22, outliers_22_table,
                 outliers_drifted_table)
    create_map_with_all_data(full_map, glider_22_cleaned, area_to_plot_1=(-18.1, -17.85, 28.40, 28.70),
                             drifted_22=drifted_22, area_to_plot_drifted=(-19, -17.85, 26.5, 28.75))
    common_analysis_tools.create_travel_map(full_map, glider_22_cleaned, (-18.1, -17.85, 28.40, 28.70))
    common_analysis_tools.create_weather_plot(weather_22, "Visualización del clima de los datos de la misión \n "
                                                      "de 2022 cercanos a los deltas lávicos.", "/clima_22.jpg")
    common_analysis_tools.create_weather_plot(weather_drifted_22, "Visualización del clima de los datos de la misión \n "
                                                              "de 2022 alejados a los deltas lávicos.",
                                          "/clima_desviado_22.jpg")
    common_analysis_tools.create_weather_mean_daily_plot(daily_22,
                                                     "Visualización de medias por hora de los datos del clima de \n"
                                                     "la misión 2022 cercanos a los deltas lávicos.",
                                                     "/visualización_de_media_diaria_clima_22.jpg")
    common_analysis_tools.create_weather_mean_daily_plot(daily_22_drifted,
                                                     "Visualización de medias por hora de los datos del clima de \n"
                                                     "la misión 2022 lejanos a los deltas lávicos.",
                                                     "/visualización_de_media_diaria_clima_22_alejado.jpg")


def create_first_map(full_map: GeoPandasMap, glider_22_cleaned: WaveGliderV2Ocean,
                     glider_22_original: WaveGliderV2Ocean) -> None:
    visualizer = MatplotlibMapChartCreator(1, 2, (15, 10))
    coord_params = define_first_map_params(glider_22_cleaned, glider_22_original)
    visualizer.add_map_to_plots(full_map, "label", ["orangered", "darkgreen"])
    visualizer.create_map(coord_params, "Limpieza de datos del recorrido Wave Glider SV2 de 2022")
    MatplotlibFigureStorer().store(RESULTS_DIRECTORY + "/recorrido_glider_2022.jpg")


def get_weather_data(col_renames: dict[str, str], glider_out_route_date: str):
    weather_22 = (extract_weather_data(define_weather_etl(["TimeStamp"], "%m/%d/%Y %I:%M %p", [0, 3, 4, 5, 6, 8, 9]))
                  .rename_columns(col_renames)
                  .filter_column("TimeStamp", operator.lt, glider_out_route_date)
                  .sort_values("TimeStamp")
                  .load())
    weather_drifted_22 = (
        extract_weather_data(define_weather_etl(["TimeStamp"], "%m/%d/%Y %I:%M %p", [0, 3, 4, 5, 6, 8, 9]))
        .rename_columns(col_renames)
        .filter_column("TimeStamp", operator.gt, glider_out_route_date)
        .sort_values("TimeStamp")
        .load())
    daily_22 = (extract_weather_data(define_weather_etl(["TimeStamp"], "%m/%d/%Y %I:%M %p", [0, 3, 4, 5, 6, 8, 9]))
                .rename_columns(col_renames)
                .filter_column("TimeStamp", operator.lt, glider_out_route_date)
                .compute_average_per_timestamp("TimeStamp")
                .sort_values("TimeStamp")
                .load())
    daily_22_drifted = (
        extract_weather_data(define_weather_etl(["TimeStamp"], "%m/%d/%Y %I:%M %p", [0, 3, 4, 5, 6, 8, 9]))
        .rename_columns(col_renames)
        .filter_column("TimeStamp", operator.gt, glider_out_route_date)
        .compute_average_per_timestamp("TimeStamp")
        .sort_values("TimeStamp")
        .load())
    return weather_22, daily_22, weather_drifted_22, daily_22_drifted


def extract_weather_data(etl: ETL) -> ETL:
    return etl.extract(DATA_DIR + "/WG_220202_220318/MERGED_WEATHER.csv")


def define_weather_etl(parse_dates: list[str], date_format: str, relevant_cols_idx: list[int]) -> ETL:
    return ETL(CSVPandasExtractor(parse_dates, date_format, relevant_cols_idx), PandasTransformer(),
               PandasWaveGliderWeatherLoader())


def get_ctd_22_data(cols_renames: dict[str, str], drifted_glider_date: str) \
        -> tuple[WaveGliderV2Ocean, WaveGliderV2Ocean, WaveGliderV2Ocean]:
    glider_22_cleaned = (common_analysis_tools.define_etl_glider(["TimeStamp"], '%m/%d/%Y %I:%M %p',
                                                                 [0, 2, 3, 4, 5, 6, 7, 8])
                         .extract(DATA_DIR + "/WG_220202_220318/MERGED_CTD_withOxygenCalc.csv")
                         .rename_columns(cols_renames)
                         .filter_column("TimeStamp", operator.lt, drifted_glider_date)
                         .filter_column("Pressure_d", operator.gt, 0)
                         .sort_values("TimeStamp")
                         .load())
    drifted_22 = (common_analysis_tools.define_etl_glider(["TimeStamp"], '%m/%d/%Y %I:%M %p',
                                                          [0, 2, 3, 4, 5, 6, 7, 8])
                  .extract(DATA_DIR + "/WG_220202_220318/MERGED_CTD_withOxygenCalc.csv")
                  .rename_columns(cols_renames)
                  .filter_column("TimeStamp", operator.gt, drifted_glider_date)
                  .filter_column("Pressure_d", operator.gt, 0)
                  .sort_values("TimeStamp")
                  .load())
    glider_22_original = (common_analysis_tools.define_etl_glider(["TimeStamp"], '%m/%d/%Y %I:%M %p',
                                                                  [0, 2, 3, 4, 5, 6, 7, 8])
                          .extract(DATA_DIR + "/WG_220202_220318/MERGED_CTD_withOxygenCalc.csv")
                          .rename_columns(cols_renames)
                          .sort_values("TimeStamp")
                          .load())
    return glider_22_cleaned, glider_22_original, drifted_22


def analyze_data(wave_glider_22: WaveGliderV2Ocean, weather_22: WaveGliderV2Weather,
                 drifted_22: WaveGliderV2Ocean, drifted_weather: WaveGliderV2Weather,
                 outliers_22: Table, outliers_drifted_22: Table) -> None:
    glider_analyzer = PandasWaveGliderV2OceanAnalyzer()
    weather_analyzer = PandasWaveGliderV2WeatherAnalyzer()
    (CsvPandasStorer(format_dict=common_analysis_tools.define_variable_renames_to_spanish())
     .store(glider_analyzer.describe(wave_glider_22),
            RESULTS_DIRECTORY + "./datos_glider_22.csv", STORE_DATE_FORMAT, True)
     .store(glider_analyzer.analyze_null_and_unique_values(wave_glider_22),
            RESULTS_DIRECTORY + "./conteo_glider_22.csv", STORE_DATE_FORMAT, True, True, ["indexes"])
     .store(glider_analyzer.data_continuity(wave_glider_22, 100),
            RESULTS_DIRECTORY + "./continuidad_fechas_glider_22.csv", STORE_DATE_FORMAT, False)
     .store(outliers_22, RESULTS_DIRECTORY + "./outliers_wg2_22.csv", STORE_DATE_FORMAT, True,)
     .store(outliers_drifted_22, RESULTS_DIRECTORY + "./outliers_wg2_desviado_22.csv", STORE_DATE_FORMAT, True)
     .store(glider_analyzer.describe(drifted_22),
            RESULTS_DIRECTORY + "./datos_desviado_22.csv", STORE_DATE_FORMAT, True)
     .store(glider_analyzer.analyze_null_and_unique_values(drifted_22),
            RESULTS_DIRECTORY + "./conteo_desviado_22.csv", STORE_DATE_FORMAT, True, True, ["indexes"])
     .store(glider_analyzer.data_continuity(drifted_22, 100),
            RESULTS_DIRECTORY + "./continuidad_fechas_desviado_22.csv", STORE_DATE_FORMAT, False)
     .store(weather_analyzer.describe(weather_22),
            RESULTS_DIRECTORY + "./datos_clima_22.csv", STORE_DATE_FORMAT, True)
     .store(weather_analyzer.analyze_null_and_unique_values(weather_22),
            RESULTS_DIRECTORY + "./conteo_clima_22.csv", STORE_DATE_FORMAT, True, True, ["indexes"])
     .store(weather_analyzer.data_continuity(weather_22, 100),
            RESULTS_DIRECTORY + "./continuidad_fechas_clima_22.csv", STORE_DATE_FORMAT, False)
     .store(weather_analyzer.describe(drifted_weather),
            RESULTS_DIRECTORY + "./datos_clima_22_desviado.csv", STORE_DATE_FORMAT, True)
     .store(weather_analyzer.analyze_null_and_unique_values(drifted_weather),
            RESULTS_DIRECTORY + "./conteo_clima_22_desviado.csv", STORE_DATE_FORMAT, True, True, ["indexes"])
     .store(weather_analyzer.data_continuity(drifted_weather, 100),
            RESULTS_DIRECTORY + "./continuidad_fechas_clima_22_desviado.csv", STORE_DATE_FORMAT, False)
     )


def define_weather_preprocess_variables() -> tuple[dict[str, str], str]:
    return common_analysis_tools.define_wave_glider_weather_variable_renames(), '2022-03-09 15:30:00'


def create_map_with_all_data(full_map: GeoPandasMap, glider_22_cleaned: WaveGliderV2Ocean,
                             area_to_plot_1: tuple[float, float, float, float], drifted_22: WaveGliderV2Ocean,
                             area_to_plot_drifted: tuple[float, float, float, float]) -> None:
    create_full_data_map(area_to_plot_1, full_map, glider_22_cleaned,
                         "Datos en el recorrido de la misión de 2022 \n para cada una las variables consideradas",
                         "recorrido_con_datos_glider_22")
    create_full_data_map(area_to_plot_drifted, full_map, drifted_22,
                         "Datos en el recorrido de la misión de 2022 \n para cada una las variables consideradas",
                         "recorrido_desviado_con_datos_glider_22")


def create_full_data_map(area_to_plot, full_map, glider_22, title: str, store_name: str) -> None:
    plot_params = common_analysis_tools.define_data_colored_map_params(glider_22, area_to_plot)
    visualizer = MatplotlibMapChartCreator(2, 2, (20, 20))
    visualizer.add_map_to_plots(full_map, "label", ["orangered", "darkgreen"])
    visualizer.create_map_with_data(plot_params, title)
    MatplotlibFigureStorer().store(RESULTS_DIRECTORY + "/" + store_name + ".jpg")

def define_22_preprocess_variables() -> tuple[dict[str, str], str]:
    return common_analysis_tools.define_wave_glider_ocean_variable_renames(), '2022-03-09 15:30:00'


def define_first_map_params(cleaned_data: WaveGliderV2Ocean, glider22_data: WaveGliderV2Ocean) -> \
        list[LimitedPlotParams]:
    return [
        LimitedPlotParams(BasicPlotParams(glider22_data.longitude_deg, glider22_data.latitude_deg,
                                          'Datos antes de preprocesar'), LimitedPlotArea(-19, -17.85, 26.5, 28.75)),
        LimitedPlotParams(
            BasicPlotParams(cleaned_data.longitude_deg, cleaned_data.latitude_deg,
                            "Datos después del preprocesado"), LimitedPlotArea(-18.1, -17.85, 28.4, 28.70))]


def get_ctd_clean_21_data(cols_renames: dict[str, str], glider_drift_start_date: str) \
        -> WaveGliderV2Ocean:
    cleaned_21_data = (common_analysis_tools.define_etl_glider(["TimeStamp"], "%m/%d/%Y %I:%M %p",
                                                               [0, 2, 3, 4, 5, 6, 7, 8])
                       .extract(DATA_DIR + "/WG_211009_211124/MERGED_CTD_withOxygenCalc.csv")
                       .rename_columns(cols_renames)
                       .filter_column("TimeStamp", operator.lt, glider_drift_start_date)
                       .sort_values("TimeStamp")
                       .load())
    return cleaned_21_data


def define_21_preprocess_variables_for_clean_data() -> tuple[dict[str, str], str]:
    return common_analysis_tools.define_wave_glider_ocean_variable_renames(), '2021-11-09 15:30:00'


main()
