from itertools import chain

from model.PredictorResult import PredictorResult


class DataWindowManager:

    def generate_window(self, window_size: int, x: list, y: list) -> (list, list):
        x = self.__create_windows(window_size, x)
        y = self.__create_windows(window_size, y)
        return x, y

    def generate_window_train_test(self, window_size: int, x: list, y: list) -> (list, list, list, list):
        x_train = self.__create_windows(window_size, x[:round(len(x) * 0.66)])
        y_train = self.__create_windows(window_size, y[:round(len(y) * 0.66)])
        x_test = self.__create_windows(window_size, x[round(len(x) * 0.66):])
        y_test = self.__create_windows(window_size, y[round(len(y) * 0.66):])
        return x_train, y_train, x_test, y_test

    def __create_windows(self, window_size: int, variables: list) -> list:
        if type(variables[0]) == list:
            variables, window_size = self.__adjust_multivariable_parameters(variables, window_size)
        return [variables[i * window_size:(i + 1) * window_size] for i in
                range((len(variables) // window_size))]

    def __adjust_multivariable_parameters(self, variables: list, window_size: int) -> (list, list):
        variables_flattened = [
            value
            for values in variables
            for value in values
        ]
        return variables_flattened, (window_size * len(variables[0]))

    def reverse_windows(self, prediction: PredictorResult) -> PredictorResult:
        prediction.y_true = list(chain.from_iterable(prediction.y_true))[1:]
        prediction.y_pred = list(chain.from_iterable(prediction.y_pred))[:-1]
        return prediction
