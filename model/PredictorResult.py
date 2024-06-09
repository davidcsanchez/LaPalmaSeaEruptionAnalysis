from typing import Union


class PredictorResult:
    def __init__(self, x: list[float], y_true: Union[list[float], list[list[float]]],
                 y_pred: Union[list[float], list[list[float]]], error: float) -> None:
        self.x = x
        self.y_true = y_true
        self.y_pred = y_pred
        self.error = error
