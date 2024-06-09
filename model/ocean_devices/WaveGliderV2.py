from model.ocean_devices import WaveGliderV2Ocean
from model.ocean_devices.WaveGliderV2Weather import WaveGliderV2Weather


class WaveGliderV2:
    def __init__(self, ocean: WaveGliderV2Ocean, weather: WaveGliderV2Weather) -> None:
        self.ocean = ocean
        self.weather = weather
