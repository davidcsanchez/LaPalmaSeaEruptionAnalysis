from model.params.BasicPlotParams import BasicPlotParams
from model.params.ColorParams import ColorParams
from model.params.LimitedPlotArea import LimitedPlotArea


class ScatterColoredParams:
    def __init__(self, basic_plot_params: BasicPlotParams, colored_plot_params: ColorParams,
                 limited_area: LimitedPlotArea):
        self.basic_plot_params = basic_plot_params
        self.colored_plot_params = colored_plot_params
        self.limited_area = limited_area
