from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error

from model.PredictorResult import PredictorResult


class SklearnElasticNetModel:

    def __init__(self, alpha=0.0001):
        self.clf = ElasticNet(alpha=alpha)

    def predict(self, x: list[float], y_true: list[float]) -> PredictorResult:
        y_pred = list(self.clf.predict(x))
        return PredictorResult(x, y_true, y_pred, mean_squared_error(y_true, y_pred))

    def train(self, x: list[float], y_true: list[float]) -> None:
        self.clf.fit(x, y_true)
