from typing import Iterable

from sklearn.model_selection import train_test_split


class SklearnDataSplitter:
    def split(self, x: Iterable, y: Iterable, test_size=0.33):
        return train_test_split(x, y, test_size=test_size, random_state=42)
