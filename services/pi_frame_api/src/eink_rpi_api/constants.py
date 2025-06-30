from enum import Enum

ENV_CONFIG_PATH = "CONFIG_PATH"

class EpdType(Enum):
    WaveShare13BlackWhite960x680 = ("WaveShare13BlackWhite960x680", 960, 680)
    WaveShare13BlackGreyWhite960x680 = ("WaveShare13BlackGreyWhite960x680", 960, 680)
    WaveShare13BlackRedWhite960x680 = ("WaveShare13BlackRedWhite960x680", 960, 680)
    WaveShare13FullColor1600x1200 = ("WaveShare13FullColor1600x1200", 1600, 1200)

    def __init__(self, label, width, height):
        self.label = label
        self.width = width
        self.height = height

    @classmethod
    def from_label(cls, label: str):
        for member in cls:
            if member.label == label:
                return member
        raise ValueError(f"{label} is not a valid EpdType label.")
