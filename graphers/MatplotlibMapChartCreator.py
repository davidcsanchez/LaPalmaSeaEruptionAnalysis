import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib.colors import ListedColormap, Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm

from model.GeoPandasMap import GeoPandasMap
from model.params.LimitedPlotArea import LimitedPlotArea
from model.params.compound_params.LimitedPlotParams import LimitedPlotParams
from model.params.compound_params.ScatterColoredParams import ScatterColoredParams


class MatplotlibMapChartCreator:

    def __init__(self, n_rows: int, n_cols: int, fig_size: tuple[int, int]):
        self.norm = None
        self.fig, self.ax_list = plt.subplots(n_rows, n_cols, figsize=fig_size, squeeze=False)
        if isinstance(self.ax_list, np.ndarray):
            self.ax_list = self.ax_list.ravel()
        else:
            self.ax_list = [self.ax_list]
        self.ax_list_iterable = iter(self.ax_list)

    def create_map(self, coord_params: list[LimitedPlotParams], title: str) -> None:
        list(map(self.__scatter_coordinate_ax, coord_params))
        self.fig.suptitle(title, fontsize=30)
        plt.tight_layout()

    def create_map_with_data(self, plot_params: list[ScatterColoredParams], title: str) -> None:
        list(map(self.scatter_coordinate_ax_colored, plot_params))
        self.fig.suptitle(title, fontsize=30)
        plt.tight_layout()

    def create_map_with_data_directions(self, plot_params: list[ScatterColoredParams], title: str) -> None:
        list(map(self.scatter_coordinate_ax_colored_with_direction, plot_params))
        self.fig.suptitle(title, fontsize=30)
        plt.tight_layout()

    def __scatter_coordinate_ax(self, params: LimitedPlotParams) -> None:
        ax = next(self.ax_list_iterable)
        ax.scatter(params.basic_plot_params.x, params.basic_plot_params.y, s=0.1, c="darkblue")
        self.__set_plot_frame(ax)
        self.__set_ax_lims(ax, params.limited_area)
        self.__set_ax_tick_labels_size(ax)
        self.__set_ax_background(ax, 'lavender')
        ax.set_title(params.basic_plot_params.title, fontdict={'fontsize': 20})

    def scatter_coordinate_ax_colored(self, params: ScatterColoredParams) -> None:
        ax = next(self.ax_list_iterable)
        self.__set_plot_frame(ax)
        self.__set_ax_lims(ax, params.limited_area)
        ax.set_title(params.basic_plot_params.title, fontdict={'fontsize': 20})
        plot = ax.scatter(params.basic_plot_params.x,
                          params.basic_plot_params.y,
                          c=params.colored_plot_params.colour_data,
                          cmap=params.colored_plot_params.cmap, s=10)
        self.__add_colorbar(ax, params, plot)
        self.__set_ax_tick_labels_size(ax)
        self.__set_ax_background(ax, params.colored_plot_params.background_color)
        return plot

    def scatter_coordinate_ax_colored_with_direction(self, params: ScatterColoredParams) -> None:
        ax = next(self.ax_list_iterable)
        self.__set_plot_frame(ax)
        self.__set_ax_lims(ax, params.limited_area)
        ax.set_title(params.basic_plot_params.title, fontdict={'fontsize': 20})
        arrow_step = 15
        norm_val, pos_x, pos_y, u, v = self.__define_angles_for_directions(params, arrow_step)
        self.norm = Normalize()
        self.norm.autoscale(list(params.colored_plot_params.colour_data[::arrow_step]))
        plot = ax.quiver(pos_x, pos_y, u / norm_val, v / norm_val, angles="xy", zorder=5, pivot="mid",
                         color=cm.viridis(self.norm(params.colored_plot_params.colour_data[::arrow_step])), scale=20)
        self.__add_colorbar(ax, params, plot)
        self.__set_ax_tick_labels_size(ax)
        plt.subplots_adjust(left=0.16, bottom=0.1, right=0.8, top=0.9, wspace=0.5, hspace=0.2)
        self.__set_ax_background(ax, params.colored_plot_params.background_color)
        return plot

    def __add_colorbar(self, ax, params: ScatterColoredParams, plot) -> None:
        if max(params.colored_plot_params.colour_data) > 1000:
            self.__set_colorbar_scientific_notation(ax, params, plot)
        else:
            self.__set_colorbar(ax, params, plot)

    def __define_angles_for_directions(self, params: ScatterColoredParams, step: int):
        x = params.basic_plot_params.x[::step]
        y = params.basic_plot_params.y[::step]
        u = np.diff(x)
        v = np.diff(y)
        pos_x = x[:-1] + u / 2
        pos_y = y[:-1] + v / 2
        norm_val = np.sqrt(u ** 2 + v ** 2)
        return norm_val, pos_x, pos_y, u, v

    def __set_plot_frame(self, ax: Axes) -> None:
        ax.set_aspect('equal')
        ax.set_xlabel('Longitud', fontsize=18)
        ax.set_ylabel('Latitud', fontsize=18)

    def __set_colorbar_scientific_notation(self, ax: Axes, params: ScatterColoredParams, plot: PathCollection) -> None:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        col_bar = plt.colorbar(plot, ax=ax, cax=cax, label=params.colored_plot_params.colored_label, format=self.__format_number_colbar)
        col_bar.ax.tick_params(labelsize=18)
        col_bar.set_label(label=params.colored_plot_params.colored_label, fontsize=18)

    def __set_colorbar(self, ax: Axes, params: ScatterColoredParams, plot: PathCollection) -> None:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        col_bar = plt.colorbar(plot, ax=ax, cax=cax,
                               label=params.colored_plot_params.colored_label
                               )
        col_bar.ax.tick_params(labelsize=18)
        col_bar.set_label(label=params.colored_plot_params.colored_label, fontsize=18)

    def __format_number_colbar(self, x, pos):
        if self.norm is not None: x = self.norm.inverse(x)
        a, b = '{:.4e}'.format(x).split('e')
        b = int(b)
        return r'${}x10^{{{}}}$'.format(a, b)

    def add_map_to_plots(self, geo_pandas_map: GeoPandasMap, legend_column: str, legend_colors: list[str]):
        list(map(lambda ax: geo_pandas_map.plot(ax=ax, column=legend_column, legend=True,
                                                cmap=ListedColormap(legend_colors),
                                                legend_kwds={"fontsize": 15}), self.ax_list))

    def __set_ax_lims(self, ax, params: LimitedPlotArea) -> None:
        ax.set_xlim(params.x_min, params.x_max)
        ax.set_ylim(params.y_min, params.y_max)

    def __set_ax_tick_labels_size(self, ax) -> None:
        ax.tick_params(axis='x', labelsize=16, labelrotation=20)
        ax.tick_params(axis='y', labelsize=16)

    def __set_ax_background(self, ax, color: str) -> None:
        ax.set_facecolor(color)
