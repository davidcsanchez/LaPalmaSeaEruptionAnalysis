import numpy as np


class NumpyPrimitiveDataAnalyzer:

    def analyze_intercuartilic_thresholds(self, values: list[float]) -> tuple[float, float, float, float]:
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        return (q1 - 1.5 * iqr), q1, q3, (q3 + 1.5 * iqr)
