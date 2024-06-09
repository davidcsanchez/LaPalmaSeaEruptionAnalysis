from datetime import datetime

from model.params.BasicPlotParams import BasicPlotParams
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.MarkerParams import MarkerParams
from model.params.SpikesParams import SpikesParams


class PlotStylishSpikesParams:
    def __init__(self, basic_plot_params: BasicPlotParams, marker_params: MarkerParams, limit_params: LimitedPlotArea,
                 spikes_params: SpikesParams):
        self.basic_plot_params = basic_plot_params
        self.marker_params = marker_params
        self.limit_params = limit_params
        self.spike_params = spikes_params
