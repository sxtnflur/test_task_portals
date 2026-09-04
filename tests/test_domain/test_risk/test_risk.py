import pytest

from domain.common.errors import DomainValueError, ValueObjectValueError
from domain.portal.value_objects.energy import Energy
from domain.portal.value_objects.stability import PortalStability
from domain.risk import RiskFactorEnum, RiskLevel
from domain.risk import Risk


@pytest.mark.parametrize("value", [0, 5, 10])
def test_accepts_values_within_bounds(value):
    assert Risk(value).value == value


@pytest.mark.parametrize("value", [-1, 11])
def test_rejects_values_out_of_bounds(value):
    with pytest.raises(DomainValueError):
        Risk(value)


def test_rejects_non_int_value():
    with pytest.raises(ValueObjectValueError):
        Risk(5.0)


def test_has_no_factors_by_default():
    assert Risk(0).factors == ()
    assert Risk(0).main_risk_factor is None


@pytest.mark.parametrize(
    "value, expected_level",
    [(0, RiskLevel.low), (3, RiskLevel.low), (4, RiskLevel.middle), (6, RiskLevel.middle), (7, RiskLevel.high), (10, RiskLevel.high)],
)
def test_level_boundaries(value, expected_level):
    assert Risk(value).level == expected_level


class TestAssess:
    def test_safe_portal_has_zero_risk_and_no_factors(self, make_expires_at):
        # Must be exactly full (10.0): anything below that is "middle" or
        # "critical" instability and gets flagged as a `high_instability`
        # factor, per `Risk.assess()`.
        risk = Risk.assess(
            stability=PortalStability(10.0),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=300),
        )

        assert risk.value == 0
        assert risk.level == RiskLevel.low
        assert risk.factors == ()
        assert risk.main_risk_factor is None

    def test_high_instability_is_flagged_and_drives_the_score(self, make_expires_at):
        # Stability stays above its min (0.0) - at the min it would trip the
        # emergency override tested in `TestEmergencyOverride` below.
        risk = Risk.assess(
            stability=PortalStability(0.5),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=300),
        )

        assert risk.value == 6
        assert risk.level == RiskLevel.middle
        assert risk.has_factor(RiskFactorEnum.high_instability)
        assert not risk.has_factor(RiskFactorEnum.high_energy)
        assert not risk.has_factor(RiskFactorEnum.closing_soon)
        assert risk.main_risk_factor.name == RiskFactorEnum.high_instability

    def test_high_energy_is_not_flagged_as_a_factor(self, make_expires_at):
        # Energy never produces a `RiskFactor` (unlike stability/expiry) -
        # it only ever feeds the weighted formula below.
        risk = Risk.assess(
            stability=PortalStability(9.0),
            energy=Energy(8),
            expires_at=make_expires_at(minutes=300),
        )

        assert risk.value == 3
        assert not risk.has_factor(RiskFactorEnum.high_energy)

    def test_closing_soon_is_flagged_and_drives_the_score(self, make_expires_at):
        # 45 seconds: inside the closing-soon window (<=60s) but outside the
        # emergency window (<=30s, see `TestEmergencyOverride`), so the
        # formula - not the override - drives the score here.
        risk = Risk.assess(
            stability=PortalStability(9.0),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=0.75),
        )

        assert risk.value == 1
        assert risk.has_factor(RiskFactorEnum.closing_soon)
        assert risk.main_risk_factor.name == RiskFactorEnum.closing_soon

    def test_factors_are_sorted_by_priority_descending(self, make_expires_at):
        # Energy stays at its max just to show it no longer contributes a
        # factor even here - risk still reaches 10, but via the stability
        # emergency below, not from energy.
        risk = Risk.assess(
            stability=PortalStability(0.0),
            energy=Energy(10),
            expires_at=make_expires_at(minutes=1),
        )

        assert [factor.name for factor in risk.factors] == [
            RiskFactorEnum.high_instability,
            RiskFactorEnum.closing_soon,
        ]
        priorities = [factor.priority for factor in risk.factors]
        assert priorities == sorted(priorities, reverse=True)
        assert risk.value == 10
        assert risk.level == RiskLevel.high

    def test_two_factors_still_sorted_by_priority(self, make_expires_at):
        # 45 seconds: inside the closing-soon window but outside the
        # emergency window, so both factors coexist without either being
        # capped away by the stability/expiry overrides.
        risk = Risk.assess(
            stability=PortalStability(2.0),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=0.75),
        )

        assert risk.value == 6
        assert [factor.name for factor in risk.factors] == [
            RiskFactorEnum.high_instability,
            RiskFactorEnum.closing_soon,
        ]
        assert risk.main_risk_factor.name == RiskFactorEnum.high_instability


class TestEmergencyOverride:
    """Stability at its min, or under 30s to expiry, force risk to 10
    regardless of what the weighted formula would otherwise compute.
    Energy has no such override - see `test_energy_at_max_does_not_force_max_risk`."""

    def test_energy_at_max_does_not_force_max_risk(self, make_expires_at):
        # Unlike stability/expiry, energy has no emergency override: even at
        # its max, risk keeps tracking the weighted formula so it stays
        # responsive to other changes instead of getting stuck at 10.
        risk = Risk.assess(
            stability=PortalStability(8.0),
            energy=Energy(10),
            expires_at=make_expires_at(minutes=300),
        )

        assert risk.value == 4
        assert risk.level == RiskLevel.middle
        assert not risk.has_factor(RiskFactorEnum.high_energy)

    def test_stability_at_min_forces_max_risk(self, make_expires_at):
        # Zero stability is also well past `is_critical()`'s threshold, so
        # (unlike the energy case above) this override keeps its factor.
        risk = Risk.assess(
            stability=PortalStability(0.0),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=300),
        )

        assert risk.value == 10
        assert risk.level == RiskLevel.high
        assert risk.has_factor(RiskFactorEnum.high_instability)

    def test_expiring_in_under_30_seconds_forces_max_risk(self, make_expires_at):
        # Without the override this would score low: stability/energy are safe
        # and only 24s to expiry.
        risk = Risk.assess(
            stability=PortalStability(8.0),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=0.4),
        )

        assert risk.value == 10
        assert risk.level == RiskLevel.high

    def test_expiring_in_exactly_30_seconds_forces_max_risk(self, make_expires_at):
        risk = Risk.assess(
            stability=PortalStability(8.0),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=0.5),
        )

        assert risk.value == 10

    def test_expiring_just_above_30_seconds_does_not_force_max_risk(self, make_expires_at):
        risk = Risk.assess(
            stability=PortalStability(8.0),
            energy=Energy(0),
            expires_at=make_expires_at(minutes=31 / 60),
        )

        assert risk.value == 2
