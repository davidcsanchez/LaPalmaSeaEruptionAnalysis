from typing import Iterable

import numpy as np
from matplotlib import pyplot as plt

from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.compound_params.PlotStylishParams import PlotStylishParams
from model.params.compound_params.PlotStylishSpikesParams import PlotStylishSpikesParams


class MatplotlibFigureCreator:

    def __init__(self, n_rows: int, n_cols: int, fig_size: tuple[int, int], graph_title: int = 16,
                 fig_title_size: int = 16) -> None:
        self.__ax_label_size = 12
        self.__ax_title = graph_title
        self.__fig_title_size = fig_title_size
        self.fig, self.ax_list = plt.subplots(n_rows, n_cols, figsize=fig_size)
        self.__convert_to_only_1_array()
        self.ax_list_iterable = iter(self.ax_list)
        self.plot_horizontal_lines = []

    def __convert_to_only_1_array(self) -> None:
        if isinstance(self.ax_list, np.ndarray):
            self.ax_list = self.ax_list.ravel()
        else:
            self.ax_list = [self.ax_list]

    def create_timeseries(self, plots_line_params: list[PlotStylishParams],
                          plot_scatter_params: list[PlotStylishParams], title: str,
                          timeseries_ticks: list) -> None:
        self.__configure_fig_text(title)
        self.__configure_fig_legend(self.__get_line_graphs(plots_line_params),
                                    self.__get_scatter_plots(plot_scatter_params))
        self.__set_timeseries_ticks(timeseries_ticks)
        self.fig.tight_layout()

    def create_timeseries_with_outliers(self, plots_line_params: list[PlotStylishParams],
                                        plot_scatter_params: list[PlotStylishSpikesParams], title: str,
                                        timestamps: list) -> None:
        self.__configure_fig_text(title)
        self.__configure_fig_legend(self.__get_line_graphs(plots_line_params),
                                    self.__get_scatter_plots_with_spikes(plot_scatter_params))
        self.__set_timeseries_ticks(timestamps)
        self.fig.tight_layout()

    def create_timeseries_different_x_ticks(self, plots_line_params: list[PlotStylishParams],
                                            plot_scatter_params: list[PlotStylishParams], title: str,
                                            timeseries_ticks: list[list]) -> None:
        self.__configure_fig_text(title)
        self.__configure_fig_legend(self.__get_line_graphs(plots_line_params),
                                    self.__get_scatter_plots(plot_scatter_params))
        self.__set_multiple_timeseries_ticks(timeseries_ticks)
        self.fig.tight_layout()

    def create_correlations(self, plots_line_params: list[tuple[PlotStylishParams, PlotStylishParams]],
                            plots_scatter_params: list[tuple[PlotStylishParams, PlotStylishParams]],
                            title: str,
                            x_ticks: list[list[any]]) -> None:
        self.__configure_fig_text(title)
        self.__correlations_ax_list()
        lines = self.__get_line_graphs([plot for tuple_of_plots in plots_line_params for plot in tuple_of_plots])
        scatters = self.__get_scatter_plots(
            [plot for tuple_of_plots in plots_scatter_params for plot in tuple_of_plots])
        self.__configure_fig_legend(scatters, lines)
        self.__set_x_ticks_for_correlations(x_ticks)
        self.fig.tight_layout()

    def create_daily_means(self, plots_line_params: list[PlotStylishParams],
                           plot_scatter_params: list[PlotStylishParams], title: str,
                           timeseries_ticks) -> None:
        self.__configure_fig_text(title)
        self.__configure_fig_legend(self.__get_line_graphs(plots_line_params),
                                    self.__get_scatter_plots(plot_scatter_params))
        self.__set_daily_ticks(timeseries_ticks)
        self.fig.tight_layout()

    def add_hortizontal_lines(self, y_values: list[float], color: str, label: str) -> None:
        for i, ax in enumerate(self.ax_list):
            ax.axhline(y=y_values[i], xmin=0, xmax=1, color=color, label=label)
            if i + 1 == len(self.ax_list):
                self.plot_horizontal_lines.append(ax.axhline(y=y_values[i], xmin=0, xmax=1, color=color, label=label))

    def add_hortizontal_lines_to_legend(self) -> None:
        self.fig.legend(handles=self.plot_horizontal_lines,
            fontsize=13)

    def __configure_fig_legend(self, scatter_plots: list, line_plots: list) -> None:
        self.fig.legend(
            handles=scatter_plots + line_plots,
            fontsize=13)

    def __configure_fig_text(self, title: str) -> None:
        self.fig.supylabel("Medidas", fontsize=20)
        self.fig.supxlabel("Timestamp", fontsize=20)
        self.fig.suptitle(title, fontsize=self.__fig_title_size)

    def __get_line_graphs(self, plots_line_params: list) -> list:
        return list(map(self.__extract_plot, map(self.__get_plot, plots_line_params)))

    def __get_scatter_plots(self, plot_scatter_plots: list) -> list:
        return list(map(self.__get_scatter_plot, plot_scatter_plots))

    def __extract_plot(self, plot_list: list):
        return plot_list[0]

    def __get_plot(self, params: PlotStylishParams):
        ax = next(self.ax_list_iterable)
        ax.tick_params(axis='y', labelcolor=params.marker_params.color, labelsize=self.__ax_label_size)
        self.__set_ax_lims(ax, params.limit_params)
        ax.set_title(params.basic_plot_params.title, fontsize=self.__ax_title)
        return ax.plot(params.basic_plot_params.x, params.basic_plot_params.y,
                       color=params.marker_params.color,
                       label=params.marker_params.label,
                       linestyle=params.marker_params.style,
                       markersize=params.marker_params.mark_size)

    def __get_scatter_plot(self, params: PlotStylishParams):
        ax = next(self.ax_list_iterable)
        ax.tick_params(axis='y', labelcolor=params.marker_params.color, labelsize=self.__ax_label_size)
        self.__set_ax_lims(ax, params.limit_params)
        ax.set_title(params.basic_plot_params.title, fontsize=self.__ax_title)
        return ax.scatter(x=params.basic_plot_params.x, y=params.basic_plot_params.y,
                          color=params.marker_params.color,
                          label=params.marker_params.label,
                          s=params.marker_params.mark_size)

    def __get_scatter_with_spikes_plot(self, params: PlotStylishSpikesParams):
        ax = next(self.ax_list_iterable)
        ax.tick_params(axis='y', labelcolor=params.marker_params.color, labelsize=self.__ax_label_size)
        self.__set_ax_lims(ax, params.limit_params)
        ax.set_title(params.basic_plot_params.title, fontsize=self.__ax_title)
        main_plot = ax.scatter(x=params.basic_plot_params.x, y=params.basic_plot_params.y,
                               color=params.marker_params.color,
                               label=params.marker_params.label,
                               s=params.marker_params.mark_size)
        ax.scatter(x=params.spike_params.spikes_indexes, y=params.spike_params.spikes_values,
                   color=params.spike_params.spike_colour, s=params.marker_params.mark_size * 2.5, edgecolors='black')
        for index in params.spike_params.spikes_indexes:
            ax.axvline(index, color=params.spike_params.spike_colour, alpha=0.3)
        return main_plot

    def __set_x_ticks(self, ax, x_ticks_idx: Iterable, x_ticks_labels: Iterable, rotation: int) -> None:
        ax.set_xticks(x_ticks_idx)
        ax.set_xticklabels(x_ticks_labels, rotation=rotation)

    def __set_ax_lims(self, ax, params: LimitedPlotArea) -> None:
        ax.set_xlim(params.x_min, params.x_max)
        ax.set_ylim(params.y_min, params.y_max)

    def __set_timeseries_ticks(self, x) -> None:
        list(map(lambda ax: self.__set_x_ticks(ax, x_ticks_idx=(np.arange(0, len(x), 300)),
                                               x_ticks_labels=([date.date() for date in x][::300]),
                                               rotation=20)
                 , self.__get_axs_list()))

    def __get_axs_list(self):
        return self.ax_list if isinstance(self.ax_list, np.ndarray) else self.ax_list

    def set_three_plotters_one_figure(self) -> None:
        ax3 = self.__get_host_plotter().twinx()
        ax3.spines["right"].set_position(('outward', 60))
        self.ax_list = [self.__get_host_plotter(), self.__get_host_plotter().twinx(), ax3]
        self.ax_list_iterable = iter(self.ax_list)

    def __get_host_plotter(self):
        return self.__get_axs_list()[0]

    def __set_daily_ticks(self, timeseries_ticks: Iterable) -> None:
        plt.xticks(ticks=np.arange(0, len(timeseries_ticks), 20),
                   labels=[date for date in timeseries_ticks][::20], rotation=20)

    def __correlations_ax_list(self) -> None:
        new_ax_list = []
        for ax in self.ax_list:
            new_ax_list.append(ax)
            new_ax_list.append(ax.twinx())
        self.ax_list = new_ax_list
        self.ax_list_iterable = iter(self.ax_list)

    def __set_x_ticks_for_correlations(self, x_ticks: list[list[zip]]) -> None:
        for x, ax in zip(x_ticks, self.ax_list[::2]):
            self.__set_x_ticks(ax, x_ticks_idx=(np.arange(0, len(x), round(len(x) / 20))),
                               x_ticks_labels=([date.date() for date in x][::round(len(x) / 20)]),
                               rotation=20)

    def __set_multiple_timeseries_ticks(self, timeseries_ticks) -> None:
        for x, ax in zip(timeseries_ticks, self.ax_list):
            self.__set_x_ticks(ax, x_ticks_idx=(np.arange(0, len(x), round(len(x) / 20))),
                               x_ticks_labels=([date.date() for date in x][::round(len(x) / 20)]),
                               rotation=20)

    def __get_scatter_plots_with_spikes(self, plot_scatter_params: list[PlotStylishSpikesParams]):
        return [self.__get_scatter_with_spikes_plot(params,) for params in plot_scatter_params]
