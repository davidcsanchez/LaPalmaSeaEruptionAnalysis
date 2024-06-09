import joblib
import keras
from keras import Sequential
from keras.src.layers import Dense, Dropout
from sklearn.metrics import mean_squared_error

from model.PredictorResult import PredictorResult


class KerasLSTMModel:

    def __init__(self, input_dim: int, output_dim: int, epochs: int, learning_rate: float, hidden_size: int, lstm_units: int, batch_size: int = 32):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.learning_rate = learning_rate
        self.optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.epochs = epochs
        self.hidden_size = hidden_size
        self.batch_size = batch_size
        self.lstm_units = lstm_units
        keras.utils.set_random_seed(812)

    def train(self, x, y):
        self.model = self.__define_model()
        self.model.fit(x, y, epochs=self.epochs, batch_size=self.batch_size, verbose=1)

    def predict(self, x, y_true):
        y_pred = list(self.model.predict(x).reshape(-1, self.output_dim))
        return PredictorResult(x, y_true, y_pred, mean_squared_error(y_true, y_pred))

    def __define_model(self):
        inputs = keras.layers.Input(shape=(self.input_dim, 1,))
        lstm_out = keras.layers.LSTM(self.lstm_units)(inputs)
        intermediate = keras.layers.Dense(self.hidden_size)(lstm_out)
        outputs = keras.layers.Dense(self.output_dim)(intermediate)
        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(loss=keras.losses.mean_squared_error, optimizer=self.optimizer, metrics=['accuracy'])
        return model

    def save_model(self):
        self.model.save("model.h5")
