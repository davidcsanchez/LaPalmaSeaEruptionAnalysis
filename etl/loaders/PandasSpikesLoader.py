import pandas as pd

from model.Spikes import Spikes
from model.Table import Table


class PandasSpikesLoader:

    def load(self, df: pd.DataFrame) -> Spikes:
        return Spikes([Spikes.SpikeVariable(value) for value in df["Variable"]], df["Threshold"].iloc[0],
                      # We take first threshold of different values, because it is not used for preprocess after loading
                      list(df["TimeStamp"].dt.to_pydatetime()),
                      list(df["Values"]), list(df.index))
