import pytest

from application import PortalNotFoundError
from application.portal.dto import PortalInfo, RiskInfo, ShortPortalInfo, UpdatedPortal
from domain.change_logs import PortalChangeLogAction
from domain.common.errors import DomainValueError
from domain.portal.enums import PortalActionEnum, PortalStatusEnum
from domain.portal.errors import ClosedPortalError
from domain.risk import RiskLevel


class TestGetPortals:
    async def test_returns_empty_list_when_no_portals_exist(self, portal_service):
        assert await portal_service.get_portals() == []

    async def test_maps_each_portal_to_a_short_info(self, portal_service, portal_repository, make_portal):
        # Stability stays below its max (10.0) - at the max, Risk.assess()
        # now forces the maximum risk level regardless of other factors.
        portal = make_portal(
            portal_id=1, name="Alpha", world_destination="Mars", stability=9.0, energy=0, expires_in_minutes=300
        )
        portal_repository.seed(portal)

        result = await portal_service.get_portals()

        assert result == [
            ShortPortalInfo(
                id=1,
                name="Alpha",
                world_destination="Mars",
                expired_at=portal.expires_at.value,
                expired=False,
                status=PortalStatusEnum.open,
                observers=0,
                energy=0,
                stability=9.0,
                risk_level=RiskLevel.low,
                marked=False,
            )
        ]

    async def test_risk_level_is_none_for_a_closed_portal(self, portal_service, portal_repository, make_portal):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        [info] = await portal_service.get_portals()

        assert info.status == PortalStatusEnum.closed
        assert info.risk_level is None
        # `Portal.energy`/`.stability` report 0 once closed.
        assert info.energy == 0
        assert info.stability == 0.0

    async def test_respects_offset_and_limit(self, portal_service, portal_repository, make_portal):
        for i in range(1, 4):
            portal_repository.seed(make_portal(portal_id=i))

        result = await portal_service.get_portals(offset=1, limit=1)

        assert [info.id for info in result] == [2]


class TestGetPortal:
    async def test_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.get_portal(999)

    async def test_returns_full_info_including_risk(self, portal_service, portal_repository, make_portal):
        # Stability stays above its min (0.0) - at the min, Risk.assess()
        # now forces the maximum risk value regardless of other factors.
        portal = make_portal(portal_id=1, stability=0.5, energy=0, expires_in_minutes=300)
        portal_repository.seed(portal)

        info = await portal_service.get_portal(1)

        assert info == PortalInfo(
            id=1,
            name=portal.name,
            world_destination=portal.world_destination,
            expired_at=portal.expires_at.value,
            expired=False,
            status=PortalStatusEnum.open,
            observers=0,
            energy=0,
            stability=0.5,
            risk=RiskInfo(
                level=RiskLevel.middle,
                value=6,
                factors=portal.get_risk().factors,
                recommended_action=PortalActionEnum.stabilize,
            ),
            marked=False,
        )

    async def test_closed_portal_has_no_risk_and_nothing_recommended(
        self, portal_service, portal_repository, make_portal
    ):
        portal = make_portal(stability=0.0, energy=9)
        portal.close()
        portal_repository.seed(portal)

        info = await portal_service.get_portal(1)

        assert info.status == PortalStatusEnum.closed
        assert info.energy == 0
        assert info.stability == 0.0
        assert info.risk == RiskInfo(level=None, value=0, factors=(), recommended_action=PortalActionEnum.open)

    async def test_portal_expired_at_construction_starts_closed_and_returns_cleanly(
        self, portal_service, portal_repository, make_portal
    ):
        # A portal already past its expiry the moment it's constructed comes
        # out of `Portal.__init__` already `closed` - so this goes through
        # the same "closed" path as the test above, rather than raising:
        # unlike the old `Portal.risk` property, `get_risk()` never raises.
        portal_repository.seed(make_portal(expires_in_minutes=-1))

        info = await portal_service.get_portal(1)

        assert info.status == PortalStatusEnum.closed
        assert info.risk.level is None
        assert info.risk.recommended_action == PortalActionEnum.open


class TestGetBestAction:
    async def test_delegates_to_the_portal(self, portal_service, portal_repository, make_portal):
        portal_repository.seed(make_portal(stability=10.0, energy=0, expires_in_minutes=300))

        assert await portal_service.get_best_action(1) == PortalActionEnum.add_observers

    async def test_returns_open_for_a_closed_portal(self, portal_service, portal_repository, make_portal):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        assert await portal_service.get_best_action(1) == PortalActionEnum.open

    async def test_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.get_best_action(999)

    async def test_does_not_persist_the_portal(self, portal_service, portal_repository, make_portal):
        portal_repository.seed(make_portal())

        await portal_service.get_best_action(1)

        assert portal_repository.saved == []


class TestOpen:
    async def test_reopens_a_closed_portal_and_returns_updated_state(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        result = await portal_service.open(1)

        assert isinstance(result, UpdatedPortal)
        assert result.portal.status == PortalStatusEnum.open
        assert result.change_log.action == PortalChangeLogAction.opened
        assert result.change_log.portal_id == 1
        assert portal.status == PortalStatusEnum.open
        assert portal_repository.saved == [portal]
        assert change_logs_repository.logs == [result.change_log]

    async def test_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.open(999)

    async def test_propagates_domain_error_when_already_open(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal_repository.seed(make_portal())

        with pytest.raises(DomainValueError):
            await portal_service.open(1)

        assert portal_repository.saved == []
        assert change_logs_repository.logs == []


class TestClose:
    async def test_closes_an_open_portal_and_returns_updated_state(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal_repository.seed(make_portal())

        result = await portal_service.close(1)

        assert result.portal.status == PortalStatusEnum.closed
        assert result.portal.energy == 0
        assert result.portal.risk.recommended_action == PortalActionEnum.open
        assert result.change_log.action == PortalChangeLogAction.closed
        assert portal_repository.saved[0].status == PortalStatusEnum.closed

    async def test_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.close(999)

    async def test_propagates_domain_error_when_observers_are_present(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.add_observer()
        portal_repository.seed(portal)

        with pytest.raises(DomainValueError):
            await portal_service.close(1)

        assert portal_repository.saved == []
        assert change_logs_repository.logs == []

    async def test_propagates_domain_error_when_already_closed(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        with pytest.raises(DomainValueError):
            await portal_service.close(1)

        assert change_logs_repository.logs == []


class TestStabilize:
    async def test_increases_stability_and_returns_updated_state(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal_repository.seed(make_portal(stability=2.0))

        result = await portal_service.stabilize(1)

        assert result.portal.stability == pytest.approx(2.1)
        assert portal_repository.saved[0].stability.value == pytest.approx(2.1)
        assert result.change_log.action == PortalChangeLogAction.stabilize

    async def test_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.stabilize(999)

    async def test_propagates_closed_portal_error(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        with pytest.raises(ClosedPortalError):
            await portal_service.stabilize(1)

        assert portal_repository.saved == []
        assert change_logs_repository.logs == []


class TestObservers:
    async def test_add_observer_increments_and_returns_updated_state(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal_repository.seed(make_portal())

        result = await portal_service.add_observer(1)

        assert result.portal.observers == 1
        assert portal_repository.saved[0].count_observers == 1
        assert result.change_log.action == PortalChangeLogAction.added_observer

    async def test_add_observer_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.add_observer(999)

    async def test_add_observer_propagates_closed_portal_error(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        with pytest.raises(ClosedPortalError):
            await portal_service.add_observer(1)

        assert portal_repository.saved == []
        assert change_logs_repository.logs == []

    async def test_take_observer_decrements_and_returns_updated_state(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.add_observer()
        portal_repository.seed(portal)

        result = await portal_service.take_observer(1)

        assert result.portal.observers == 0
        assert portal_repository.saved[0].count_observers == 0
        assert result.change_log.action == PortalChangeLogAction.taken_observer

    async def test_take_observer_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.take_observer(999)

    async def test_take_observer_propagates_domain_error_when_none_present(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal_repository.seed(make_portal())

        with pytest.raises(DomainValueError):
            await portal_service.take_observer(1)

        assert portal_repository.saved == []
        assert change_logs_repository.logs == []

    async def test_take_observer_propagates_closed_portal_error(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        with pytest.raises(ClosedPortalError):
            await portal_service.take_observer(1)


class TestMarking:
    async def test_mark_returns_updated_state(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal_repository.seed(make_portal())

        result = await portal_service.mark(1)

        assert portal_repository.saved[0].marked is True
        assert result.change_log.action == PortalChangeLogAction.marked

    async def test_mark_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.mark(999)

    async def test_mark_propagates_closed_portal_error(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        with pytest.raises(ClosedPortalError):
            await portal_service.mark(1)

        assert change_logs_repository.logs == []

    async def test_unmark_returns_updated_state(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.mark()
        portal_repository.seed(portal)

        result = await portal_service.unmark(1)

        assert portal_repository.saved[0].marked is False
        assert result.change_log.action == PortalChangeLogAction.unmarked

    async def test_unmark_raises_when_portal_is_missing(self, portal_service):
        with pytest.raises(PortalNotFoundError):
            await portal_service.unmark(999)

    async def test_unmark_propagates_closed_portal_error(
        self, portal_service, portal_repository, change_logs_repository, make_portal
    ):
        portal = make_portal()
        portal.close()
        portal_repository.seed(portal)

        with pytest.raises(ClosedPortalError):
            await portal_service.unmark(1)

        assert change_logs_repository.logs == []
