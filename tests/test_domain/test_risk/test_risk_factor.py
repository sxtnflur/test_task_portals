import dataclasses

import pytest

from domain.risk import RiskFactorEnum
from domain.risk import RiskFactor


def test_priority_is_value_times_weight():
    factor = RiskFactor(RiskFactorEnum.high_instability, value=0.8, weight=0.6)

    assert factor.priority == pytest.approx(0.48)


def test_is_frozen():
    factor = RiskFactor(RiskFactorEnum.high_energy, value=1.0, weight=0.25)

    with pytest.raises(dataclasses.FrozenInstanceError):
        factor.value = 0.5


def test_equal_when_all_fields_match():
    a = RiskFactor(RiskFactorEnum.closing_soon, value=0.9, weight=0.15)
    b = RiskFactor(RiskFactorEnum.closing_soon, value=0.9, weight=0.15)

    assert a == b
