import math
from typing import Union

from AnalysisCommonTools import AnalysisCommonTools
from analyzers.SciPyCorrelationAnalyzer import SciPyCorrelationAnalyzer
from graphers.MatplotlibFigureCreator import MatplotlibFigureCreator
from model.Table import Table
from model.ocean_devices.Seabed import Seabed
from model.ocean_devices.WaveGliderV2 import WaveGliderV2
from model.ocean_devices.WaveGliderV2Ocean import WaveGliderV2Ocean
from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather
from model.params.BasicPlotParams import BasicPlotParams
from model.params.CorrelationInput import CorrelationInput
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.MarkerParams import MarkerParams
from model.params.compound_params.PlotStylishParams import PlotStylishParams
from storer.CsvPandasStorer import CsvPandasStorer
from storer.MatplotlibFigureStorer import MatplotlibFigureStorer

DATA_DIR = "./data"
RESULTS_DIRECTORY = "./results/correlation"
STORE_DATE_FORMAT = "%d/%m/%Y %H:%M"
exploratory_tools = AnalysisCommonTools(DATA_DIR, RESULTS_DIRECTORY, STORE_DATE_FORMAT)


def main_correlation():
    (ocean_21, weather_21, glider_21, ocean_22, weather_22, glider_22,
     drifted_ocean_22, glider_drifted_22, seabed_23, seabed_24) = exploratory_tools.get_data()
    cond_temp, ocean_temp_weather_temp, ox_sal, ox_temp, temp_sal = create_corr_tables(drifted_ocean_22, glider_21,
                                                                                       glider_22,
                                                                                       glider_drifted_22, ocean_21,
                                                                                       ocean_22,
                                                                                       seabed_23,
                                                                                       seabed_24)
    store_csv_results({"conductividad_temperatura.csv": cond_temp,
                       "oxigeno_temperatura.csv": ox_temp,
                       "oxigeno_salinidad.csv": ox_sal,
                       "temperatura_oc_temperatura_clima.csv": ocean_temp_weather_temp,
                       "temperatura_sal.csv": temp_sal})
    graph_correlations(drifted_ocean_22, glider_21, glider_22, glider_drifted_22, ocean_21, ocean_22, seabed_23,
                       seabed_24)


def graph_correlations(drifted_ocean_22, glider_21, glider_22, glider_drifted_22, ocean_21, ocean_22, seabed_23,
                       seabed_24) -> None:
    cond_temp_data = [ocean_21, ocean_22, drifted_ocean_22, seabed_23, seabed_24]
    graph(define_corr_params("Temperatura", "Conductividad", "coral", "darkolivegreen",
                             get_index(cond_temp_data), get_temp(cond_temp_data),
                             get_cond(cond_temp_data),
                             ["Misión de 2021", "Misión 2022 antes de desviarse", "Misión de 2022 tras el desvío ",
                              "Misión de 2023", "Misión de 2024"]),
          get_timestamp(cond_temp_data),
          "Correlación temperatura y conductividad.",
          "/conductividad_vs_temperatura.jpg")
    temp_sal_data = [ocean_21, ocean_22, drifted_ocean_22, seabed_23, seabed_24]
    graph(define_corr_params_with_first_sal("Salinidad", "Temperatura", "navy", "tomato",
                                            get_index(temp_sal_data), get_sal(temp_sal_data), get_temp(temp_sal_data),

                                            ["Misión de 2021", "Misión 2022 antes de desviarse",
                                             "Misión de 2022 tras el desvío ", "Misión de 2023", "Misión de 2024"]),
          get_timestamp(temp_sal_data),
          "Correlación temperatura y salinidad.",
          "/temperatura_vs_salinidad.jpg")
    ox_sal_data = [ocean_21, ocean_22, drifted_ocean_22]
    graph(define_corr_params_with_second_sal("Oxígeno", "Salinidad", "goldenrod", "indigo",
                                             get_index(ox_sal_data), get_ox(ox_sal_data),
                                             get_sal(ox_sal_data),
                                             ["Misión de 2021", "Misión 2022 antes de desviarse",
                                              "Misión de 2022 tras el desvío "]),
          get_timestamp(ox_sal_data),
          "Correlación oxígeno y salinidad.", "/oxigeno_vs_salinidad.jpg")
    ox_temp_data = [ocean_21, ocean_22, drifted_ocean_22]
    graph(define_corr_params("Oxígeno", "Temperatura", "goldenrod", "coral",
                             get_index(ox_temp_data), get_ox(ox_temp_data),
                             get_temp(ox_temp_data),
                             ["Misión de 2021", "Misión 2022 antes de desviarse", "Misión de 2022 tras el desvío "]),
          get_timestamp(ox_temp_data),
          "Correlación oxígeno y temperatura.", "/oxigeno_vs_temperatura.jpg")
    temp_temp_data = [glider_21, glider_22, glider_drifted_22]
    graph(define_corr_params("Temperatura de la \n superficie  del mar", "Temperatura del clima", "darkolivegreen",
                             "coral",
                             get_ocean_index(temp_temp_data), get_ocean_temp(temp_temp_data),
                             get_weather_temp(temp_temp_data),
                             ["Misión de 2021", "Misión 2022 antes de desviarse", "Misión de 2022 tras el desvío "]),
          get_ocean_timestamp(temp_temp_data),
          "Correlación temperatura del océano \n y temperatura del clima", "/temp_vs_temp.jpg")


def graph(corr_graph_params, timestamp: list, title: str, filename: str) -> None:
    graph_correlation(title, corr_graph_params, timestamp)
    MatplotlibFigureStorer().store(RESULTS_DIRECTORY + filename)


def get_ocean_temp(data: list[WaveGliderV2]) -> \
        list[list[float]]:
    return list(map(lambda x: x.ocean.temperature_c, data))


def get_ocean_timestamp(data: list[WaveGliderV2]) -> \
        list[list[float]]:
    return list(map(lambda x: x.ocean.timestamp, data))


def get_weather_temp(data: list[WaveGliderV2]) -> \
        list[list[float]]:
    return list(map(lambda x: x.weather.temperature_c, data))


def get_ox(data: list[WaveGliderV2Ocean]) -> \
        list[list[float]]:
    return list(map(lambda x: x.oxygen, data))


def get_cond(data: list[Union[WaveGliderV2Ocean, WaveGliderV2Weather, WaveGliderV2, Seabed]]) -> \
        list[list[float]]:
    return list(map(lambda x: x.conductivity_s_m, data))


def get_sal(data: list[Union[WaveGliderV2Ocean, WaveGliderV2Weather, WaveGliderV2, Seabed]]) -> \
        list[list[float]]:
    return list(map(lambda x: x.salinity_psu, data))


def filter_dict_keys(dic: dict, keys: list) -> dict:
    return {key: dic[key] for key in keys}


def store_csv_results(csv_results: dict) -> None:
    list(map(lambda kv: CsvPandasStorer(5).store(kv[1], RESULTS_DIRECTORY + "/" + kv[0], STORE_DATE_FORMAT, True),
             csv_results.items()))


def get_temp(data: list[Union[WaveGliderV2Ocean, WaveGliderV2Weather, WaveGliderV2, Seabed]]) -> \
        list[list[float]]:
    return list(map(lambda x: x.temperature_c, data))


def graph_correlation(title: str, params: list[tuple[PlotStylishParams, PlotStylishParams]], x_ticks: list[list]) -> None:
    chart_creator = MatplotlibFigureCreator(len(params), 1, (9, math.ceil((10 / 4) * len(params))))
    chart_creator.create_correlations(params, [], title, x_ticks)


def get_timestamp(data: list[Union[WaveGliderV2Ocean, WaveGliderV2Weather, WaveGliderV2, Seabed]]) -> \
        list[list]:
    return list(map(lambda x: x.timestamp, data))


def get_index(data: list[Union[WaveGliderV2Ocean, WaveGliderV2Weather, Seabed]]) -> \
        list[list[float]]:
    return list(map(lambda x: x.index, data))


def get_ocean_index(data: list[WaveGliderV2]) -> \
        list[list[float]]:
    return list(map(lambda x: x.ocean.index, data))


def define_corr_params(label_1: str, label_2: str, color_1: str, color_2: str, x_values: list[list[float]],
                       y_values_1: list[list[float]], y_values_2: list[list[float]], titles: list[str]) -> \
        list[tuple[PlotStylishParams, PlotStylishParams]]:
    result = [(create_plot_stylish_params(label_1, "-", color_1,
                                          x_values[0], y_values_1[0], titles[0]),
               create_plot_stylish_params(label_2, "--", color_2,
                                          x_values[0], y_values_2[0], titles[0]))]
    for i in range(1, len(x_values)):
        result.append((create_plot_stylish_params("", "-", color_1,
                                                  x_values[i], y_values_1[i], titles[i]),
                       create_plot_stylish_params("", "--", color_2,
                                                  x_values[i], y_values_2[i], titles[i])))
    return result


def define_corr_params_with_first_sal(label_1: str, label_2: str, color_1: str, color_2: str,
                                      x_values: list[list[float]],
                                      y_values_1: list[list[float]], y_values_2: list[list[float]],
                                      titles: list[str]) -> \
        list[tuple[PlotStylishParams, PlotStylishParams]]:
    y_lims = {"Misión de 2021": (36.7, 37.2), "Misión 2022 antes de desviarse": (36.7, 37),
              "Misión de 2022 tras el desvío ": (36.7, 37), "Misión de 2023": (36.5, 37), "Misión de 2024": (36.4, 37)}
    result = [(create_plot_stylish_params_with_sal(label_1, "dotted", color_1,
                                                   x_values[0], y_values_1[0], titles[0], y_lims=y_lims[titles[0]]),
               create_plot_stylish_params_with_sal(label_2, "solid", color_2,
                                                   x_values[0], y_values_2[0], titles[0]))]
    for i in range(1, len(x_values)):
        result.append((create_plot_stylish_params_with_sal("", "dotted", color_1,
                                                           x_values[i], y_values_1[i], titles[i],
                                                           y_lims=y_lims[titles[i]]),
                       create_plot_stylish_params_with_sal("", "solid", color_2,
                                                           x_values[i], y_values_2[i], titles[i])))
    return result


def define_corr_params_with_second_sal(label_1: str, label_2: str, color_1: str, color_2: str,
                                       x_values: list[list[float]],
                                       y_values_1: list[list[float]], y_values_2: list[list[float]],
                                       titles: list[str]) -> \
        list[tuple[PlotStylishParams, PlotStylishParams]]:
    y_lims = {"Misión de 2021": (36.7, 37.2), "Misión 2022 antes de desviarse": (36.7, 37),
              "Misión de 2022 tras el desvío ": (36.7, 37), "Misión de 2023": (36.5, 37), "Misión de 2024": (36.4, 37)}
    result = [(create_plot_stylish_params_with_sal(label_1, "dotted", color_1,
                                                   x_values[0], y_values_1[0], titles[0]),
               create_plot_stylish_params_with_sal(label_2, "solid", color_2,
                                                   x_values[0], y_values_2[0], titles[0], y_lims=y_lims[titles[0]]))]
    for i in range(1, len(x_values)):
        result.append((create_plot_stylish_params_with_sal("", "dotted", color_1,
                                                           x_values[i], y_values_1[i], titles[i]),
                       create_plot_stylish_params_with_sal("", "solid", color_2,
                                                           x_values[i], y_values_2[i], titles[i],
                                                           y_lims=y_lims[titles[i]])))
    return result


def create_plot_stylish_params(label: str, style: str, color: str, x_values: list, y_values: list, title: str,
                               y_lims=None, x_lims=None) -> PlotStylishParams:
    if y_lims is None:
        y_lims = y_values
    if x_lims is None:
        x_lims = x_values
    return PlotStylishParams(
        BasicPlotParams(x_values, y_values, title),
        MarkerParams(color, label, style, 1),
        get_limited_plot_params(x_lims, y_lims))


def create_plot_stylish_params_with_sal(label: str, style: str, color: str, x_values: list, y_values: list, title: str,
                                        y_lims=None, x_lims=None) -> PlotStylishParams:
    if x_lims is None:
        x_lims = x_values
    if y_lims is None:
        y_lims = y_values
        limited_params = get_limited_plot_params(x_lims, y_lims)
    else:
        limited_params = get_limited_plot_params_for_sal(x_lims, y_lims)
    return PlotStylishParams(
        BasicPlotParams(x_values, y_values, title),
        MarkerParams(color, label, style, 1),
        limited_params)


def get_limited_plot_params(x: list, y: list) -> LimitedPlotArea:
    return LimitedPlotArea(min(x), max(x), exploratory_tools.calculate_min_lim(y),
                           exploratory_tools.calculate_max_lim(y))


def get_limited_plot_params_for_sal(x: list, y: list) -> LimitedPlotArea:
    return LimitedPlotArea(min(x), max(x), exploratory_tools.calculate_min_lim_salinity(y),
                           exploratory_tools.calculate_max_lim_salinity(y))


def create_corr_tables(drifted_ocean_22, glider_21, glider_22, glider_drifted_22, ocean_21, ocean_22, seabed_23,
                       seabed_24) -> (CorrelationInput, CorrelationInput, CorrelationInput, CorrelationInput, CorrelationInput):
    inputs = {"Misión 2021": ocean_21, "Misión 2022": ocean_22,
              "Misión 2022 desviado": drifted_ocean_22, "Misión 2023": seabed_23, "Misión 2024": seabed_24,
              "Misión 2021 completa": glider_21, "Misión 2022 completa ": glider_22,
              "Misión 2022 desviado completa": glider_drifted_22}
    cond_temp = analyze_correlation(
        filter_dict_keys(inputs, ["Misión 2021", "Misión 2022", "Misión 2022 desviado", "Misión 2023", "Misión 2024"]),
        create_correlation_input_cond_temp)
    ox_temp = analyze_correlation(
        filter_dict_keys(inputs, ["Misión 2021", "Misión 2022", "Misión 2022 desviado"]),
        create_correlation_input_oxy_temp)
    ox_sal = analyze_correlation(
        filter_dict_keys(inputs, ["Misión 2021", "Misión 2022", "Misión 2022 desviado"]),
        create_correlation_input_oxy_sal)
    ocean_temp_weather_temp = analyze_correlation(
        filter_dict_keys(inputs, ["Misión 2021 completa", "Misión 2022 completa ", "Misión 2022 desviado completa"]),
        create_correlation_input_temp_temp)
    temp_sal = analyze_correlation(
        filter_dict_keys(inputs, ["Misión 2021", "Misión 2022", "Misión 2022 desviado", "Misión 2023", "Misión 2024"]),
        create_correlation_input_temp_sal)
    return cond_temp, ocean_temp_weather_temp, ox_sal, ox_temp, temp_sal


def create_correlation_input_temp_temp(label: str, data: WaveGliderV2) -> CorrelationInput:
    return CorrelationInput(data.ocean.temperature_c, data.weather.temperature_c, label)


def create_correlation_input_temp_sal(label: str, data: WaveGliderV2Ocean) -> CorrelationInput:
    return CorrelationInput(data.temperature_c, data.salinity_psu, label)


def create_correlation_input_oxy_sal(label: str, data: WaveGliderV2Ocean) -> CorrelationInput:
    return CorrelationInput(data.oxygen, data.salinity_psu, label)


def create_correlation_input_oxy_temp(label: str, data: Union[WaveGliderV2Ocean, Seabed]) -> CorrelationInput:
    return CorrelationInput(data.oxygen, data.temperature_c, label)


def analyze_correlation(inputs_dict: dict[str, Union[WaveGliderV2Ocean, WaveGliderV2Weather, Seabed]],
                        create_correlation_input: callable) -> Table:
    return SciPyCorrelationAnalyzer().analyze(
        list(map(lambda kv: create_correlation_input(*kv),
                 inputs_dict.items())))


def create_correlation_input_cond_temp(label: str, data: Union[WaveGliderV2Ocean, Seabed]) -> CorrelationInput:
    return CorrelationInput(data.conductivity_s_m, data.temperature_c, label)


def create_correlation_input_cond_oxyg(label: str, data: Union[WaveGliderV2Ocean, Seabed]) -> CorrelationInput:
    return CorrelationInput(data.oxygen, data.temperature_c, label)


main_correlation()
