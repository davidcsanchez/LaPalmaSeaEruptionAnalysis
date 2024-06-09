class CorrelationInput:
    def __init__(self, data_1: list[float], data_2: list[float], label: str) -> None:
        self.data_1 = data_1
        self.data_2 = data_2
        self.label = label
