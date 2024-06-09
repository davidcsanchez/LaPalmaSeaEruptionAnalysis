from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from model.PredictorResult import PredictorResult


class SklearnLinearRegressionModel:

    def __init__(self):
        self.clf = LinearRegression()

    def predict(self, x: list[float], y_true: list[float]) -> PredictorResult:
        y_pred = list(self.clf.predict(x))
        return PredictorResult(x, y_true, y_pred, mean_squared_error(y_true, y_pred))

    def train(self, x: list[float], y_true: list[float]) -> None:
        self.clf.fit(x, y_true)
