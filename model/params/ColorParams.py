from typing import Iterable


class ColorParams:
    def __init__(self, colour_data: Iterable, cmap: str, colored_label: str, background_color: str = "lavender"):
        self.colour_data = colour_data
        self.cmap = cmap
        self.colored_label = colored_label
        self.background_color = background_color
