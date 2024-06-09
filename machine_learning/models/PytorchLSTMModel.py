import numpy as np
import torch
from sklearn.metrics import mean_squared_error
from torch import nn, optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import DataLoader, TensorDataset

from model.PredictorResult import PredictorResult


class PytorchLSTMModel:

    def __init__(self, input_size: int, hidden_size: int, num_layers: int, epochs: int, learning_rate: float, batch_size: int):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.model = LSTMModel(input_size, hidden_size, num_layers)
        self.optimizer = optim.Adam(self.model.parameters(), lr = self.learning_rate)
        self.loss_fn = nn.MSELoss()
        self.lr_scheduler = ReduceLROnPlateau(self.optimizer, 'min', patience=200, factor=0.1, verbose=True)

    def train(self, x, y):
        loader = DataLoader(TensorDataset(torch.tensor(x, dtype=torch.float64), torch.tensor(y, dtype=torch.float64)), shuffle=False, batch_size=self.batch_size)
        for epoch in range(self.epochs):
            self.model.train()
            for X_batch, y_batch in loader:
                y_pred = self.model(X_batch)
                loss = self.loss_fn(y_pred, y_batch)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
            self.lr_scheduler.step(loss)
            print(epoch, loss)

    def predict(self, x, y_true):
        y_pred = self.model(torch.tensor(x))
        return PredictorResult(x, list(y_true), list(y_pred.detach().numpy()), mean_squared_error(y_true,
                                                                                 y_pred.detach().numpy()))


class LSTMModel(nn.Module):
    # input_size : number of features in input at each time step
    # hidden_size : Number of LSTM units
    # num_layers : number of LSTM layers
    def __init__(self, input_size: int, hidden_size: int, num_layers: int):
        super(LSTMModel, self).__init__()  # initializes the parent class nn.Module
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dtype=torch.float64)
        self.linear = nn.Linear(hidden_size, input_size, dtype=torch.float64)

    def forward(self, x):  # defines forward pass of the neural network
        out, _ = self.lstm(x)
        out = self.linear(out)
        return out


