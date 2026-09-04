import datetime
import math

import pytest

from domain.common.errors import (
    DomainUnsupportedOperandTypeError,
    DomainWrongComparisonTypeError,
    ValueObjectValueError,
)
from domain.portal.value_objects import ExpiresAt


def test_rejects_non_datetime_value():
    with pytest.raises(ValueObjectValueError):
        ExpiresAt("2024-01-01")


def test_not_expired_when_in_the_future(clock, make_expires_at):
    assert make_expires_at(minutes=30).expired is False


def test_expired_when_in_the_past(clock, make_expires_at):
    assert make_expires_at(minutes=-1).expired is True


def test_expires_in_minutes_matches_the_delta(clock, make_expires_at):
    expires_at = make_expires_at(minutes=45)

    assert expires_at.expires_in_minutes == pytest.approx(45, abs=0.01)


def test_expires_in_minutes_is_clamped_to_zero_once_expired(clock, make_expires_at):
    expires_at = make_expires_at(minutes=-10)

    assert expires_at.expires_in_minutes == 0


def test_urgency_is_maximal_right_at_expiry(clock, make_expires_at):
    assert make_expires_at(minutes=0).urgency == pytest.approx(1.0)


def test_urgency_decays_as_expiry_gets_further_away(clock, make_expires_at):
    soon = make_expires_at(minutes=5)
    later = make_expires_at(minutes=120)

    assert soon.urgency > later.urgency


def test_urgency_matches_the_closing_soon_calibration(clock, make_expires_at):
    # 30 seconds left reads as urgent, 2 minutes left reads as normal - the
    # decay is calibrated so `urgency` crosses 0.5 exactly at `CLOSING_SOON_WINDOW`.
    assert make_expires_at(minutes=0.5).urgency == pytest.approx(1 / math.sqrt(2), abs=1e-6)
    assert make_expires_at(minutes=1).urgency == pytest.approx(0.5, abs=1e-6)
    assert make_expires_at(minutes=2).urgency == pytest.approx(0.25, abs=1e-6)


def test_is_closing_soon_true_within_the_window(clock, make_expires_at):
    # 30 seconds left is already closing soon.
    assert make_expires_at(minutes=0.5).is_closing_soon() is True


def test_is_closing_soon_true_right_at_the_window_boundary(clock, make_expires_at):
    assert make_expires_at(minutes=1).is_closing_soon() is True


def test_is_closing_soon_false_outside_the_window(clock, make_expires_at):
    # 2 minutes left is still normal.
    assert make_expires_at(minutes=2).is_closing_soon() is False


def test_time_can_be_advanced_deterministically_via_clock(clock):
    expires_at = ExpiresAt(clock.now + datetime.timedelta(minutes=1))
    assert expires_at.expired is False

    clock.advance(minutes=2)

    assert expires_at.expired is True


class TestOrdering:
    def test_compares_two_expires_at_objects(self, clock, make_expires_at):
        sooner = make_expires_at(minutes=5)
        later = make_expires_at(minutes=10)

        assert sooner < later
        assert sooner <= sooner
        assert later > sooner
        assert later >= later

    def test_compares_against_a_raw_datetime(self, clock, make_expires_at):
        expires_at = make_expires_at(minutes=5)

        assert expires_at < clock.now + datetime.timedelta(minutes=10)
        assert expires_at > clock.now

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_raises_when_compared_to_an_unsupported_type(self, op, make_expires_at):
        with pytest.raises(DomainWrongComparisonTypeError):
            op(make_expires_at(), "not an expires_at")


class TestArithmetic:
    """Unlike the generic `ValueObject` arithmetic, `ExpiresAt` defines its
    own `__add__`/`__sub__`/`__radd__`/`__rsub__`: a `timedelta` shifts the
    timestamp forward/backward (used e.g. by `Portal.change_status()` to
    extend an expiry) and re-wraps the result as a new `ExpiresAt`. Anything
    else - another `ExpiresAt`, an unrelated type - is rejected.
    """

    def test_add_a_timedelta_shifts_forward(self, make_expires_at):
        result = make_expires_at(minutes=5) + datetime.timedelta(minutes=10)

        assert result == make_expires_at(minutes=15)

    def test_sub_a_timedelta_shifts_backward(self, make_expires_at):
        result = make_expires_at(minutes=15) - datetime.timedelta(minutes=10)

        assert result == make_expires_at(minutes=5)

    def test_radd_a_timedelta_shifts_forward(self, make_expires_at):
        result = datetime.timedelta(minutes=10) + make_expires_at(minutes=5)

        assert result == make_expires_at(minutes=15)

    def test_add_between_two_expires_at_raises(self, make_expires_at):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            make_expires_at(minutes=5) + make_expires_at(minutes=10)

    def test_sub_between_two_expires_at_raises(self, make_expires_at):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            make_expires_at(minutes=10) - make_expires_at(minutes=5)

    def test_add_unrelated_type_raises(self, make_expires_at):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            make_expires_at() + "not an expires_at"
