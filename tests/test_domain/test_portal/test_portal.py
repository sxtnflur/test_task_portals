import datetime

import pytest

from domain.common.errors import DomainValueError
from domain.portal.entities import Portal
from domain.portal.enums import PortalActionEnum, PortalMethodEnum, PortalStatusEnum
from domain.portal.errors import ClosedPortalError
from domain.portal.value_objects.energy import Energy
from domain.portal.value_objects import ExpiresAt
from domain.portal.value_objects.stability import PortalStability


class TestConstruction:
    def test_exposes_the_given_attributes(self, make_portal):
        portal = make_portal(
            portal_id=7, name="Gate", world_destination="Venus", stability=8.0, energy=2, expires_in_minutes=10
        )

        assert portal.id == 7
        assert portal.name == "Gate"
        assert portal.world_destination == "Venus"
        assert portal.stability == PortalStability(8.0)
        assert portal.energy.value == 2
        assert portal.count_observers == 0
        assert portal.marked is False

    def test_expires_at_and_expires_in_are_exposed(self, make_portal, clock):
        portal = make_portal(expires_in_minutes=10)

        assert portal.expires_at == ExpiresAt(clock.now + datetime.timedelta(minutes=10))
        assert portal.expires_in == datetime.timedelta(minutes=10)

    def test_open_when_expiry_is_in_the_future(self, make_portal):
        portal = make_portal(expires_in_minutes=30)

        assert portal.status == PortalStatusEnum.open
        assert portal.is_open is True
        assert portal.is_closed is False
        assert portal.expired is False

    def test_closed_when_expiry_is_already_in_the_past(self, make_portal):
        portal = make_portal(expires_in_minutes=-5)

        assert portal.status == PortalStatusEnum.closed
        assert portal.is_closed is True
        assert portal.expired is True

    def test_direct_constructor_accepts_persisted_state_verbatim(self, clock):
        expires_at = ExpiresAt(clock.now + datetime.timedelta(hours=2))

        portal = Portal(
            portal_id=5,
            name="Gate",
            world_destination="Venus",
            energy=Energy(3),
            stability=PortalStability(2.0),
            expires_at=expires_at,
            count_observers=2,
            marked=True,
            status=PortalStatusEnum.open,
        )

        assert portal.id == 5
        assert portal.count_observers == 2
        assert portal.marked is True
        assert portal.status == PortalStatusEnum.open

    def test_constructor_still_derives_closed_from_an_already_expired_expires_at(self, clock):
        # Even a status of `open` passed in explicitly is overridden once
        # `expires_at` is already in the past.
        portal = Portal(
            portal_id=1,
            name="Gate",
            world_destination="Venus",
            energy=Energy(0),
            stability=PortalStability(10.0),
            expires_at=ExpiresAt(clock.now - datetime.timedelta(minutes=1)),
            count_observers=0,
            marked=False,
            status=PortalStatusEnum.open,
        )

        assert portal.status == PortalStatusEnum.closed

    def test_create_defaults_count_observers_marked_and_status(self, clock):
        portal = Portal.create(
            portal_id=1,
            name="Gate",
            world_destination="Venus",
            energy=Energy(0),
            stability=PortalStability(10.0),
            expires_at=ExpiresAt(clock.now + datetime.timedelta(hours=2)),
        )

        assert portal.count_observers == 0
        assert portal.marked is False
        assert portal.status == PortalStatusEnum.open

    def test_create_honors_an_explicit_closed_status_when_not_expired(self, clock):
        # `__init__` only re-derives `closed` from an *already expired*
        # `expires_at`; an explicit `closed` status for a not-yet-expired
        # portal is otherwise respected.
        portal = Portal.create(
            portal_id=1,
            name="Gate",
            world_destination="Venus",
            energy=Energy(0),
            stability=PortalStability(10.0),
            expires_at=ExpiresAt(clock.now + datetime.timedelta(hours=2)),
            status=PortalStatusEnum.closed,
        )

        assert portal.status == PortalStatusEnum.closed


class TestHash:
    def test_hash_depends_only_on_id(self, make_portal):
        assert hash(make_portal(portal_id=1)) == hash(make_portal(portal_id=1))


class TestCloseAndOpen:
    def test_close_sets_status_to_closed(self, make_portal):
        portal = make_portal()
        portal.close()

        assert portal.status == PortalStatusEnum.closed

    def test_close_with_observers_present_raises(self, make_portal):
        portal = make_portal()
        portal.add_observer()

        with pytest.raises(DomainValueError):
            portal.close()

        assert portal.status == PortalStatusEnum.open

    def test_close_when_already_closed_raises(self, make_portal):
        portal = make_portal()
        portal.close()

        with pytest.raises(DomainValueError):
            portal.close()

    def test_open_reopens_a_closed_portal(self, make_portal):
        portal = make_portal()
        portal.close()
        portal.open()

        assert portal.status == PortalStatusEnum.open

    def test_open_when_already_open_raises(self, make_portal):
        portal = make_portal()

        with pytest.raises(DomainValueError):
            portal.open()


class TestStabilize:
    def test_increases_stability_by_one_tenth(self, make_portal):
        portal = make_portal(stability=2.0)

        result = portal.stabilize()

        assert result == PortalStability(2.1)
        assert portal.stability == PortalStability(2.1)

    def test_is_capped_at_ten(self, make_portal):
        portal = make_portal(stability=9.95)

        result = portal.stabilize()

        assert result == PortalStability(10.0)

    def test_raises_on_a_closed_portal(self, make_portal):
        portal = make_portal()
        portal.close()

        with pytest.raises(ClosedPortalError):
            portal.stabilize()


class TestObservers:
    def test_add_observer_increments_the_counter(self, make_portal):
        portal = make_portal()
        portal.add_observer()
        portal.add_observer()

        assert portal.count_observers == 2

    def test_add_observer_on_a_closed_portal_raises(self, make_portal):
        portal = make_portal()
        portal.close()

        with pytest.raises(ClosedPortalError):
            portal.add_observer()

    def test_take_observer_decrements_the_counter(self, make_portal):
        portal = make_portal()
        portal.add_observer()
        portal.take_observer()

        assert portal.count_observers == 0

    def test_take_observer_when_none_present_raises(self, make_portal):
        portal = make_portal()

        with pytest.raises(DomainValueError):
            portal.take_observer()

    def test_take_observer_never_goes_negative(self, make_portal):
        portal = make_portal()

        with pytest.raises(DomainValueError):
            portal.take_observer()

        assert portal.count_observers == 0

    def test_take_observer_on_a_closed_portal_raises(self, make_portal):
        portal = make_portal()
        portal.close()

        with pytest.raises(ClosedPortalError):
            portal.take_observer()


class TestMarking:
    def test_starts_unmarked(self, make_portal):
        assert make_portal().marked is False

    def test_mark_sets_marked_true(self, make_portal):
        portal = make_portal()
        portal.mark()

        assert portal.marked is True

    def test_unmark_sets_marked_false(self, make_portal):
        portal = make_portal()
        portal.mark()
        portal.unmark()

        assert portal.marked is False

    def test_mark_on_a_closed_portal_raises(self, make_portal):
        portal = make_portal()
        portal.close()

        with pytest.raises(ClosedPortalError):
            portal.mark()

    def test_unmark_on_a_closed_portal_raises(self, make_portal):
        portal = make_portal()
        portal.close()

        with pytest.raises(ClosedPortalError):
            portal.unmark()


class TestClosedPortalReporting:
    """A closed portal reports zeroed-out energy/stability/risk instead of
    whatever it held right before closing."""

    def test_energy_and_stability_read_as_zero(self, make_portal):
        portal = make_portal(stability=8.0, energy=5)
        portal.close()

        assert portal.energy == Energy(0)
        assert portal.stability == PortalStability(0.0)

    def test_expires_in_reads_as_zero(self, make_portal):
        portal = make_portal(expires_in_minutes=120)
        portal.close()

        assert portal.expires_in == datetime.timedelta(seconds=0)

    def test_get_risk_returns_none(self, make_portal):
        portal = make_portal(stability=0.0, energy=9)
        portal.close()

        assert portal.get_risk() is None


class TestGetRisk:
    def test_returns_none_when_closed(self, make_portal):
        portal = make_portal()
        portal.close()

        assert portal.get_risk() is None

    def test_available_while_open(self, make_portal):
        # Stability stays below its max (10.0) - at the max, Risk.assess()
        # now forces the maximum risk value regardless of other factors.
        portal = make_portal(stability=9.5, energy=0, expires_in_minutes=300)

        assert portal.get_risk().value == 0

    def test_available_for_a_naturally_expired_but_not_yet_closed_portal(self, make_portal, clock):
        # `status` is only recomputed at construction time; a portal that
        # expires *after* creation stays `open` (stale) until something
        # calls `close()`. `get_risk()` only special-cases `is_closed`, so
        # it keeps working here instead of raising.
        portal = make_portal(expires_in_minutes=1)
        clock.advance(minutes=2)

        assert portal.expired is True
        assert portal.is_closed is False
        assert portal.get_risk() is not None


class TestGetBestAction:
    def test_closed_portal_recommends_open(self, make_portal):
        portal = make_portal(stability=9.0, energy=0, expires_in_minutes=30)
        portal.close()

        assert portal.get_best_action() == PortalActionEnum.open

    def test_expired_portal_without_observers_should_be_closed(self, make_portal, clock):
        portal = make_portal(expires_in_minutes=1)
        clock.advance(minutes=2)

        assert portal.expired is True
        assert portal.status == PortalStatusEnum.open  # stale: never auto-synced
        assert portal.get_best_action() == PortalActionEnum.close

    def test_expired_portal_with_observers_should_be_evacuated(self, make_portal, clock):
        portal = make_portal(expires_in_minutes=1)
        portal.add_observer()
        clock.advance(minutes=2)

        assert portal.get_best_action() == PortalActionEnum.take_observers

    def test_high_instability_should_be_stabilized(self, make_portal):
        portal = make_portal(stability=0.0, energy=0, expires_in_minutes=300)

        assert portal.get_best_action() == PortalActionEnum.stabilize

    def test_high_instability_takes_priority_even_with_observers(self, make_portal):
        # Stability 4.0 is still "critical" (<=5) but keeps risk below the
        # `high` threshold, so `add_observer()` doesn't reject it outright -
        # unlike 0.0, which is the min-stability emergency (see TestGetRisk).
        portal = make_portal(stability=4.0, energy=0, expires_in_minutes=300)
        portal.add_observer()

        assert portal.get_best_action() == PortalActionEnum.stabilize

    def test_closing_soon_without_observers_should_be_closed(self, make_portal):
        portal = make_portal(stability=9.0, energy=0, expires_in_minutes=0.75)

        assert portal.get_best_action() == PortalActionEnum.close

    def test_closing_soon_with_observers_should_be_evacuated(self, make_portal):
        # Full stability (10.0): `add_observer()`'s -0.5 hit still leaves it
        # at 9.5, "middle" instability whose priority stays well below
        # closing_soon's - unlike 9.0, whose -0.5 hit tips the balance the
        # other way and makes `stabilize` win instead.
        portal = make_portal(stability=10.0, energy=0, expires_in_minutes=0.75)
        portal.add_observer()

        assert portal.get_best_action() == PortalActionEnum.take_observers

    def test_safe_portal_should_receive_observers(self, make_portal):
        # Must be exactly full (10.0): any lower stability is now flagged as
        # a `high_instability` factor (see TestEmergencyOverride in test_risk.py).
        portal = make_portal(stability=10.0, energy=0, expires_in_minutes=300)

        assert portal.get_best_action() == PortalActionEnum.add_observers


class TestDoMethod:
    @pytest.mark.parametrize(
        "method, expected_status",
        [
            (PortalMethodEnum.close, PortalStatusEnum.closed),
        ],
    )
    def test_dispatches_to_the_named_domain_method(self, make_portal, method, expected_status):
        portal = make_portal()

        portal.do_method(method)

        assert portal.status == expected_status

    def test_dispatches_mark(self, make_portal):
        portal = make_portal()

        portal.do_method(PortalMethodEnum.mark)

        assert portal.marked is True

    def test_dispatches_add_observer(self, make_portal):
        portal = make_portal()

        portal.do_method(PortalMethodEnum.add_observer)

        assert portal.count_observers == 1

    def test_propagates_the_underlying_domain_error(self, make_portal):
        portal = make_portal()
        portal.close()

        with pytest.raises(ClosedPortalError):
            portal.do_method(PortalMethodEnum.mark)
