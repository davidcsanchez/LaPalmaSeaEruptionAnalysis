from AnalysisCommonTools import AnalysisCommonTools
from analyzers.NumpyPrimitiveDataAnalyzer import NumpyPrimitiveDataAnalyzer
from graphers.MatplotlibFigureCreator import MatplotlibFigureCreator
from model.ocean_devices.Seabed import Seabed
from model.Table import Table
from model.ocean_devices.WaveGliderV2Ocean import WaveGliderV2Ocean
from model.params.BasicPlotParams import BasicPlotParams
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.MarkerParams import MarkerParams
from model.params.compound_params.PlotStylishParams import PlotStylishParams
from storer.CsvPandasStorer import CsvPandasStorer
from storer.MatplotlibFigureStorer import MatplotlibFigureStorer

DATA_DIR = "./data"
RESULTS_DIR = "./results/temporal"
common_tools = AnalysisCommonTools(DATA_DIR, RESULTS_DIR, None)


def main():
    (ocean_21, weather_21, glider_21, ocean_22, weather_22, glider_22,
     drifted_ocean_22, glider_drifted_22, seabed_23, seabed_24) = common_tools.get_data()

    salinity_data = ocean_21, ocean_22, drifted_ocean_22, seabed_23, seabed_24
    limits_sal = graph(salinity_data, create_salinity_plot_params(*salinity_data), "Evolución de los niveles de salinidad.",
          "/salinidad.jpg", (9, 14), "Salinity_PSU")

    oxygen_data = ocean_21, ocean_22, drifted_ocean_22
    limits_ox = graph(oxygen_data, create_oxygen_plot_params(*oxygen_data),
          "Evolución de los niveles de oxígeno.", "/oxígeno.jpg", (10, 10), "Oxygen_umol_L")

    temp_data = ocean_21, ocean_22, drifted_ocean_22, seabed_23, seabed_24
    limits_temp = graph(temp_data, create_temp_plot_params(*temp_data),
          "Evolución de los niveles de temperatura.", "/temperatura.jpg", (9, 14), "Temperature_C")
    limits_table = limits_sal.concat_equal_tables(limits_ox).concat_equal_tables(limits_temp)
    (CsvPandasStorer(format_dict=common_tools.define_variable_renames_to_spanish())
     .store(limits_table,
            RESULTS_DIR + "./limites_intercuartilicos.csv",
            None, False, True, ["Variable"]))


def add_intercuartilic_thresholds(figure_creator: MatplotlibFigureCreator, params: list[PlotStylishParams]) \
        -> tuple[float, float]:
    all_y_values = [y_value for param in params for y_value in param.basic_plot_params.y]
    lower_limit, q1, q3, upper_limit = NumpyPrimitiveDataAnalyzer().analyze_intercuartilic_thresholds(all_y_values)
    figure_creator.add_hortizontal_lines([lower_limit] * len(params), "darkviolet", "Límite inferior")
    figure_creator.add_hortizontal_lines([upper_limit] * len(params), "seagreen", "Límite superior")
    figure_creator.add_hortizontal_lines_to_legend()
    return lower_limit, upper_limit


def graph(object_data, params: list[PlotStylishParams],
          title: str, filename: str, fig_size: tuple[int, int], variable: str) -> Table:
    figure_creator = MatplotlibFigureCreator(len(object_data), 1, fig_size)
    (figure_creator
     .create_timeseries_different_x_ticks(params, [], title, get_timestamp(object_data)))
    lower_limit, upper_limit = add_intercuartilic_thresholds(figure_creator, params)
    MatplotlibFigureStorer().store(RESULTS_DIR + filename)
    return Table([Table.Column("Variable", [variable]),
                  Table.Column("Límite inferior", [lower_limit]),
                  Table.Column("límite superior", [upper_limit])], None)



def create_salinity_plot_params(ocean_21: WaveGliderV2Ocean, ocean_22: WaveGliderV2Ocean,
                                drifted_ocean_22: WaveGliderV2Ocean, seabed_23: Seabed, seabed_24: Seabed) \
        -> [PlotStylishParams]:
    return [PlotStylishParams(
        BasicPlotParams(ocean_21.index, ocean_21.salinity_psu, "Misión de 2021"),
        MarkerParams("indigo", "", "-", 1),
        get_limited_plot_params_for_sal(ocean_21.index, [36.8, 37.2])),
        PlotStylishParams(
            BasicPlotParams(ocean_22.index, ocean_22.salinity_psu, "Misión de 2022 antes de desviarse"),
            MarkerParams("indigo", "", "-", 1),
            get_limited_plot_params_for_sal(ocean_22.index, [36.8, 36.9])),
        PlotStylishParams(
            BasicPlotParams(drifted_ocean_22.index, drifted_ocean_22.salinity_psu, "Misión de 2022 tras desviarse"),
            MarkerParams("indigo", "", "-", 1),
            get_limited_plot_params_for_sal(drifted_ocean_22.index, [36.8, 37])),
        PlotStylishParams(
            BasicPlotParams(seabed_23.index, seabed_23.salinity_psu, "Misión de 2023"),
            MarkerParams("indigo", "", "-", 1),
            get_limited_plot_params_for_sal(seabed_23.index, [36.2, 37.1])),
        PlotStylishParams(
            BasicPlotParams(seabed_24.index, seabed_24.salinity_psu, "Misión de 2024"),
            MarkerParams("indigo", "", "-", 1),
            get_limited_plot_params_for_sal(seabed_24.index, [36.2, 37.1]))
    ]


def create_temp_plot_params(ocean_21: WaveGliderV2Ocean, ocean_22: WaveGliderV2Ocean,
                            drifted_ocean_22: WaveGliderV2Ocean, seabed_23: Seabed, seabed_24: Seabed) \
        -> [PlotStylishParams]:
    return [PlotStylishParams(
        BasicPlotParams(ocean_21.index, ocean_21.temperature_c, "Misión de 2021"),
        MarkerParams("coral", "", "-", 1),
        get_limited_plot_params(ocean_21.index, ocean_21.temperature_c)),
        PlotStylishParams(
            BasicPlotParams(ocean_22.index, ocean_22.temperature_c, "Misión de 2022 antes de desviarse"),
            MarkerParams("coral", "", "-", 1),
            get_limited_plot_params(ocean_22.index, ocean_22.temperature_c)),
        PlotStylishParams(
            BasicPlotParams(drifted_ocean_22.index, drifted_ocean_22.temperature_c, "Misión 2022 tras desviarse"),
            MarkerParams("coral", "", "-", 1),
            get_limited_plot_params(drifted_ocean_22.index, drifted_ocean_22.temperature_c)),
        PlotStylishParams(
            BasicPlotParams(seabed_23.index, seabed_23.temperature_c, "Misión de 2023"),
            MarkerParams("coral", "", "-", 1),
            get_limited_plot_params(seabed_23.index, seabed_23.temperature_c)),
        PlotStylishParams(
            BasicPlotParams(seabed_24.index, seabed_24.temperature_c, "Misión de 2024"),
            MarkerParams("coral", "", "-", 1),
            get_limited_plot_params(seabed_24.index, seabed_24.temperature_c))
    ]


def create_oxygen_plot_params(ocean_21: WaveGliderV2Ocean, ocean_22: WaveGliderV2Ocean,
                              drifted_ocean_22: WaveGliderV2Ocean) -> list[PlotStylishParams]:
    return [PlotStylishParams(
        BasicPlotParams(ocean_21.index, ocean_21.oxygen, "Misión 2021"),
        MarkerParams("goldenrod", "", "-", 1),
        get_limited_plot_params(ocean_21.index, [150, 220])),
        PlotStylishParams(
            BasicPlotParams(ocean_22.index, ocean_22.oxygen, "Misión 2022 antes de desviarse"),
            MarkerParams("goldenrod", "", "-", 1),
            get_limited_plot_params(ocean_22.index, [100, 230])),
        PlotStylishParams(
            BasicPlotParams(drifted_ocean_22.index, drifted_ocean_22.oxygen, "Misión 2022 tras desviado"),
            MarkerParams("goldenrod", "", "-", 1),
            get_limited_plot_params(drifted_ocean_22.index, [180, 240]))
    ]


def get_limited_plot_params(x: list, y: list) -> LimitedPlotArea:
    return LimitedPlotArea(min(x), max(x), common_tools.calculate_min_lim(y), common_tools.calculate_max_lim(y))


def get_limited_plot_params_for_sal(x: list, y: list) -> LimitedPlotArea:
    return LimitedPlotArea(min(x), max(x), common_tools.calculate_min_lim_salinity(y),
                           common_tools.calculate_max_lim_salinity(y))


def get_timestamp(salinity_data):
    return list(map(lambda x: x.timestamp, salinity_data))


main()
