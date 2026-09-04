from dataclasses import dataclass

from domain.risk.enums import RiskFactorEnum


@dataclass(frozen=True)
class RiskFactor:
    name: RiskFactorEnum
    value: float
    """Current normalized level (0..1) of the underlying condition."""
    weight: float
    """Configurable influence of this factor on the overall risk."""

    @property
    def priority(self) -> float:
        """How strongly this factor is pushing the risk up: value * weight."""
        return self.value * self.weight
