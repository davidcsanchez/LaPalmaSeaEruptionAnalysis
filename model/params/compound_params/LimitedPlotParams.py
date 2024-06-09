from model.params.BasicPlotParams import BasicPlotParams
from model.params.LimitedPlotArea import LimitedPlotArea


class LimitedPlotParams:
    def __init__(self, basic_plot_params: BasicPlotParams, limited_area: LimitedPlotArea):
        self.basic_plot_params = basic_plot_params
        self.limited_area = limited_area
