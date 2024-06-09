from typing import Union

import numpy as np

from machine_learning.model_preprocessors import SklearnStandardScaler
from machine_learning.models.KerasLSTMModel import KerasLSTMModel
from machine_learning.models.SklearnElasticNetModel import SklearnElasticNetModel
from machine_learning.models.SklearnLinearRegressionModel import SklearnLinearRegressionModel
from model.PredictorResult import PredictorResult


class ModelManager:

    def __init__(self, scaler: SklearnStandardScaler,
                 models: dict[str, Union[SklearnElasticNetModel, SklearnLinearRegressionModel, KerasLSTMModel]]):
        self.scaler = scaler
        self.models = models

    def train(self, x_train, y_train) -> None:
        x_train = self.scaler.fit_transform(x_train)
        list(map(lambda model: model.train(np.array(x_train), np.array(y_train)), self.models.values()))

    def predict(self, x_test, y_test) -> dict[str, PredictorResult]:
        x_test = self.scaler.transform(x_test)
        result = {}
        for model_name, model in self.models.items():
            result[model_name] = model.predict(np.array(x_test), np.array(y_test))
        return result


