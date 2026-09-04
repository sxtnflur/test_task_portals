import datetime

from domain.common.value_object import ValueObject
from domain.common.errors import DomainValueError, ValueObjectValueError

from domain.portal.value_objects.energy import Energy
from domain.portal.value_objects.expires_at import ExpiresAt
from domain.portal.value_objects.stability import PortalStability
from domain.risk.enums import RiskFactorEnum, RiskLevel
from domain.risk.value_objects.risk_factor import RiskFactor

CRITICAL_EXPIRY_WINDOW = datetime.timedelta(seconds=30)
MAX_RISK_VALUE = 10


class Risk(ValueObject):
    # Configurable influence of each factor on the overall risk score.
    INSTABILITY_WEIGHT = 0.60
    ENERGY_WEIGHT = 0.25
    URGENCY_WEIGHT = 0.15

    def __init__(self, value: int, *, factors: tuple[RiskFactor, ...] = ()):
        if not isinstance(value, int):
            raise ValueObjectValueError(self, int)

        if value < 0 or value > 10:
            raise DomainValueError("Risk can be only between 0 and 10")

        super().__init__(value)
        self.__factors = tuple(factors)

    @property
    def level(self):
        if self.value < 4:
            return RiskLevel.low
        if self.value < 7:
            return RiskLevel.middle
        return RiskLevel.high

    @property
    def high(self):
        return self.level == RiskLevel.high

    @property
    def middle(self):
        return self.level == RiskLevel.middle

    @property
    def low(self):
        return self.level == RiskLevel.low

    @property
    def factors(self) -> tuple[RiskFactor, ...]:
        """Critical conditions behind this risk level, ordered by priority (highest first)."""
        return self.__factors

    @property
    def main_risk_factor(self) -> RiskFactor | None:
        return self.__factors[0] if self.__factors else None

    def has_factor(self, name: RiskFactorEnum) -> bool:
        return any(factor.name == name for factor in self.__factors)

    @classmethod
    def assess(
        cls,
        stability: PortalStability,
        energy: Energy,
        expires_at: ExpiresAt
    ) -> 'Risk':
        instability = 1 - stability.value / 10  # 0..1
        energy_factor = energy.value / 10  # 0..1
        urgency = expires_at.urgency

        factors = []

        if (stability_level := stability.level()) in ('middle', 'critical'):
            factors.append(RiskFactor(RiskFactorEnum.high_instability, instability, cls.INSTABILITY_WEIGHT))

        if expires_at.is_closing_soon():
            factors.append(RiskFactor(RiskFactorEnum.closing_soon, urgency, cls.URGENCY_WEIGHT))

        factors.sort(key=lambda factor: factor.priority, reverse=True)

        # Stability at its min (least stable), or the portal closes in under
        # 30 seconds - either alone is an emergency, skip the weighted
        # formula entirely. Energy has no such override: at its max it still
        # only feeds the weighted formula below, so risk keeps tracking
        # stability/expiry instead of getting stuck at 10.
        is_emergency = (
            stability.value <= stability.min_value
            or expires_at.expires_in <= CRITICAL_EXPIRY_WINDOW
        )

        if is_emergency:
            return cls(MAX_RISK_VALUE, factors=tuple(factors))

        # Нестабильность — 60%, энергия — 25%, близость закрытия — 15%.
        raw_risk = (
            cls.INSTABILITY_WEIGHT * instability
            + cls.ENERGY_WEIGHT * energy_factor
            + cls.URGENCY_WEIGHT * urgency
        )

        # Энергия в нестабильном портале опаснее, чем каждый фактор по отдельности.
        interaction = 0.20 * instability * energy_factor

        value = round(max(0, min(10, 10 * (raw_risk + interaction))))

        return cls(value, factors=tuple(factors))
