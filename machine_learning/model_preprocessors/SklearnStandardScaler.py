import numpy as np
from sklearn.preprocessing import StandardScaler


class SklearnStandardScaler:
    def __init__(self):
        self.scaler = StandardScaler()

    def fit_transform(self, x):
        return self.__reshape_output(self.scaler.fit_transform(x), x)

    def transform(self, x):
        return self.__reshape_output(self.scaler.transform(x), x)

    def __reshape_output(self, x_scaled, input_vector):
        if type(input_vector[0]) is list:
            return x_scaled.reshape(np.array(input_vector).shape)
        else:
            return x_scaled
