import operator
from datetime import timedelta

from AnalysisCommonTools import AnalysisCommonTools
from etl.ETL import ETL
from model.ocean_devices.Seabed import Seabed
from analyzers.PandasSeabedAnalyzer import PandasSeabedAnalyzer
from graphers.MatplotlibFigureCreator import MatplotlibFigureCreator
from etl.loaders.PandasSeabedLoader import PandasSeabedLoader
from model.Spikes import Spikes
from model.Table import Table
from model.params.BasicPlotParams import BasicPlotParams
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.MarkerParams import MarkerParams
from model.params.compound_params.PlotStylishParams import PlotStylishParams
from etl.transformers.PandasTransformer import PandasTransformer
from etl.extractors.CSVPandasExtractor import CSVPandasExtractor
from model.params.compound_params.PlotStylishSpikesParams import PlotStylishSpikesParams
from model.params.SpikesParams import SpikesParams
from storer.CsvPandasStorer import CsvPandasStorer
from storer.MatplotlibFigureStorer import MatplotlibFigureStorer

RESULTS_DIRECTORY = "./results/exploratory/seabed"
DATA_DIR = "./data"
STORE_DATE_FORMAT = "%d/%m/%Y %H:%M"
common_analysis_tools = AnalysisCommonTools(DATA_DIR,RESULTS_DIRECTORY,STORE_DATE_FORMAT)

def seabed_main():
    seabed_23_cleaned, daily_means_seabed_23, seabed_24_cleaned, daily_means_seabed_24 = get_data()
    analyzer = PandasSeabedAnalyzer(seabed_23_cleaned, seabed_24_cleaned)
    salinity_outliers_23 = timeseries_plot(seabed_23_cleaned,
                                           "Visualización inicial de datos de fondeo de la misión de 2023",
                                           "/visualización_inicial_fondeo_23.jpg", analyzer)
    salinity_outliers_24 = timeseries_plot(seabed_24_cleaned,
                                           "Visualización inicial de datos de fondeo de la misión de 2024",
                                           "/visualización_inicial_fondeo_24.jpg", analyzer)
    daily_means_plot(daily_means_seabed_23, "Visualización de medias por hora en datos de fondeo de la misión de 2023",
                     "/visualización_de_media_diaria_fondeo_23.jpg")
    daily_means_plot(daily_means_seabed_24, "Visualización de medias por hora en datos de fondeo de la misión de 2024",
                     "/visualización_de_media_diaria_fondeo_24.jpg")
    analyze_data(seabed_23_cleaned, "23", salinity_outliers_23.to_table())
    analyze_data(seabed_24_cleaned, "24", salinity_outliers_24.to_table())


def timeseries_plot(seabed: Seabed, graph_title: str, file_name: str, analyzer: PandasSeabedAnalyzer):
    visualizer = MatplotlibFigureCreator(3, 1, (14, 14))
    salinity_outliers = analyzer.analyze_outliers_salinity(seabed)
    (conductivity_plot_params, salinity_plot_params,
     temperature_plot_params) = define_timeseries_plot_params(seabed, salinity_outliers)
    visualizer.create_timeseries_with_outliers([temperature_plot_params, conductivity_plot_params],
                                               [salinity_plot_params], graph_title,
                                               seabed.timestamp)
    MatplotlibFigureStorer().store(RESULTS_DIRECTORY + file_name)
    return salinity_outliers


def daily_means_plot(seabed: Seabed, graph_title: str, file_name: str):
    visualizer = MatplotlibFigureCreator(1, 1, (14, 7))
    visualizer.set_three_plotters_one_figure()
    conductivity_plot_params, salinity_plot_params, temperature_plot_params = define_daily_means_plot_params(seabed)
    visualizer.create_daily_means([temperature_plot_params, conductivity_plot_params],
                                  [salinity_plot_params],
                                  graph_title,
                                  seabed.timestamp)
    MatplotlibFigureStorer().store(RESULTS_DIRECTORY + file_name)


def analyze_data(seabed: Seabed, year: str, outliers: Table):
    storer = CsvPandasStorer(format_dict=common_analysis_tools.define_variable_renames_to_spanish())
    analyzer = PandasSeabedAnalyzer()
    (storer.store(
        analyzer.describe(seabed), RESULTS_DIRECTORY + "./datos_fondeo_" + year + ".csv", STORE_DATE_FORMAT, True)
    .store(
        analyzer.analyze_null_and_unique_values(seabed),
        RESULTS_DIRECTORY + "./conteo_fondeo_" + year + ".csv", STORE_DATE_FORMAT, True, True, ["indexes"])
    .store(
        analyzer.data_continuity(seabed, 100),
        RESULTS_DIRECTORY + "./continuidad_fechas_fondeo_" + year + ".csv", STORE_DATE_FORMAT, False)
    .store(
        outliers,
        RESULTS_DIRECTORY + "./outliers_fondeo_" + year + ".csv", STORE_DATE_FORMAT, True))


def get_data():
    seabed_cleaned_23 = (define_seabed_etl(["Time"], "%d/%m/%Y %H:%M",
                                           [1, 2, 3, 4])
                         .extract(DATA_DIR + "/Fondeo_230601_230614/sbe37sm-rs232_03714295_2023_06_16.csv")
                         .rename_columns({"Time": "TimeStamp"})
                         .sort_values("TimeStamp")
                         .load())
    daily_means_seabed_23 = (define_seabed_etl(["Time"], "%d/%m/%Y %H:%M",
                                               [1, 2, 3, 4])
                             .extract(DATA_DIR + "/Fondeo_230601_230614/sbe37sm-rs232_03714295_2023_06_16.csv")
                             .rename_columns({"Time": "TimeStamp"})
                             .correct_dates("2023-06-01 15:00:00", "2023-06-01 23:15:00", "TimeStamp",
                                            timedelta(hours=0, minutes=1))
                             .compute_average_per_timestamp("TimeStamp")
                             .sort_values("TimeStamp")
                             .load())
    seabed_cleaned_24 = (define_seabed_etl(None, None,
                                           [0, 1, 2, 3, 4, 5, 6], r"\s+")
                         .extract(DATA_DIR + "/Fondeo_24/sbe37sm-rs232_03714294_2024_04_10.asc")
                         .merge_columns(["Day", "Month", "Year", "Time"], "TimeStamp", " ")
                         .parse_datetime_column("TimeStamp")
                         .filter_column("Conductivity_S_m", operator=operator.ge, value=1)
                         .sort_values("TimeStamp")
                         .load())
    daily_means_seabed_24 = (define_seabed_etl(None, None,
                                               [0, 1, 2, 3, 4, 5, 6], r"\s+")
                             .extract(DATA_DIR + "/Fondeo_24/sbe37sm-rs232_03714294_2024_04_10.asc")
                             .merge_columns(["Day", "Month", "Year", "Time"], "TimeStamp", " ")
                             .parse_datetime_column("TimeStamp")
                             .filter_column("Conductivity_S_m", operator=operator.ge, value=1)
                             .compute_average_per_timestamp("TimeStamp")
                             .sort_values("TimeStamp")
                             .load())
    return seabed_cleaned_23, daily_means_seabed_23, seabed_cleaned_24, daily_means_seabed_24


def define_seabed_etl(parse_dates: list[str] | None, date_format: str | None, relevant_cols_idx: list[int], delimiter: str = ","):
    return ETL(CSVPandasExtractor(parse_dates, date_format, relevant_cols_idx, delimiter=delimiter),
               PandasTransformer(), PandasSeabedLoader())


def define_daily_means_plot_params(seabed: Seabed):
    temperature_plot_params = PlotStylishParams(
        BasicPlotParams(seabed.index, seabed.temperature_c, ""),
        MarkerParams("coral", "Temperatura", "-", 1),
        LimitedPlotArea(None, None, 19.5, 24))
    conductivity_plot_params = PlotStylishParams(
        BasicPlotParams(seabed.index, seabed.conductivity_s_m, ""),
        MarkerParams("darkolivegreen", "Conductividad", "--", 1),
        LimitedPlotArea(None, None, 4.9, 5.5))
    salinity_plot_params = PlotStylishParams(
        BasicPlotParams(seabed.index, seabed.salinity_psu, ""),
        MarkerParams("indigo", "Salinidad", "o", 10),
        LimitedPlotArea(None, None, 36, 37.5))
    return conductivity_plot_params, salinity_plot_params, temperature_plot_params


def define_timeseries_plot_params(seabed: Seabed, salinity_outliers: Spikes):
    temperature_plot_params = PlotStylishParams(
        BasicPlotParams(seabed.index, seabed.temperature_c, "Temperatura"),
        MarkerParams("coral", "Temperatura", "-", 1),
        LimitedPlotArea(None, None, 19.5, 24))
    conductivity_plot_params = PlotStylishParams(
        BasicPlotParams(seabed.index, seabed.conductivity_s_m, "Conductividad"),
        MarkerParams("darkolivegreen", "Conductividad", "--", 1),
        LimitedPlotArea(None, None, 4.9, 5.5))
    salinity_plot_params = PlotStylishSpikesParams(
        BasicPlotParams(seabed.index, seabed.salinity_psu, "Salinidad"),
        MarkerParams("indigo", "Salinidad", "o", 10),
        LimitedPlotArea(None, None, calculate_min_lim(seabed.salinity_psu),
                        calculate_max_lim(seabed.salinity_psu)),
        SpikesParams(salinity_outliers.indexes,
                     salinity_outliers.values,
                           "red")
    )
    return conductivity_plot_params, salinity_plot_params, temperature_plot_params


def calculate_min_lim(value_list: list[float]) -> float:
    return min(value_list) - 0.005 * min(value_list)


def calculate_max_lim(value_list: list[float]) -> float:
    return max(value_list) + 0.001 * max(value_list)


def get_column_from_table(table: Table, label: str) -> list:
    for column in table.columns:
        if column.label == label:
            return column.values


seabed_main()
