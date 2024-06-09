import os

from matplotlib import pyplot as plt


class MatplotlibFigureStorer:

    def store(self, filename: str):
        self.__create_dir_if_not_exists(filename)
        plt.savefig(filename)
        return self

    def __create_dir_if_not_exists(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)