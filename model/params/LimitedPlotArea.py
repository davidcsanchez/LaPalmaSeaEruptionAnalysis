from typing import Union


class LimitedPlotArea:
    def __init__(self, x_min: Union[float, None], x_max: Union[float, None], y_min: Union[float, None], y_max: Union[float, None]):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
