from enum import StrEnum, auto


class RiskFactorEnum(StrEnum):
    high_instability = auto()
    high_energy = auto()
    closing_soon = auto()


class RiskLevel(StrEnum):
    low = auto()
    middle = auto()
    high = auto()
