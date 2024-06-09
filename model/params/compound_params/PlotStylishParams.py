from model.params.MarkerParams import MarkerParams
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.BasicPlotParams import BasicPlotParams


class PlotStylishParams:
    def __init__(self, basic_plot_params: BasicPlotParams, marker_params: MarkerParams, limit_params: LimitedPlotArea):
        self.basic_plot_params = basic_plot_params
        self.marker_params = marker_params
        self.limit_params = limit_params
