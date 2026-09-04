from application.portal.errors import PortalNotFoundError, PortalIsAlreadyMarkedError, PortalIsNotMarkedError
from application.portal.dto import PortalInfo, RiskInfo, ShortPortalInfo, UpdatedPortal, PortalsSummary
from application.change_logs.service import PortalChangeLogsService

from domain.change_logs.enums import PortalChangeLogAction
from domain.portal.entities.portal import Portal
from domain.portal.enums import PortalActionEnum, PortalMethodEnum
from domain.portal.repositories import PortalRepository
from domain.common.errors import UpdateToSameValueError


def _get_risk_info(portal: Portal) -> RiskInfo:
    """Always returns a `RiskInfo`, even for a closed portal (`get_risk()`
    is `None` there): `level`/`value`/`factors` fall back to "no risk data"
    defaults, but `recommended_action` (e.g. `nothing` for a closed portal)
    is independent of risk and always meaningful.
    """
    risk = portal.get_risk()
    return RiskInfo(
        level=risk.level if risk is not None else None,
        value=risk.value if risk is not None else 0,
        factors=risk.factors if risk is not None else (),
        recommended_action=portal.get_best_action()
    )


def _portals_to_short_info_portals(portals: list[Portal]):
    return [
            ShortPortalInfo(
                id=portal.id,
                name=portal.name,
                world_destination=portal.world_destination,
                expired=portal.expired,
                expired_at=portal.expires_at.value,
                observers=portal.count_observers,
                status=portal.status,
                energy=portal.energy.value,
                stability=portal.stability.value,
                risk_level=None if portal.is_closed else portal.get_risk().level,
                marked=portal.marked
            ) for portal in portals
        ]


class PortalService:
    """Application use cases for Portal aggregates.

    The service coordinates retrieval and persistence. Business invariants stay
    inside Portal and its value objects.
    """

    CHANGE_LOG_ACTIONS = {
        PortalMethodEnum.open: PortalChangeLogAction.opened,
        PortalMethodEnum.close: PortalChangeLogAction.closed,
        PortalMethodEnum.add_observer: PortalChangeLogAction.added_observer,
        PortalMethodEnum.take_observer: PortalChangeLogAction.taken_observer,
        PortalMethodEnum.mark: PortalChangeLogAction.marked,
        PortalMethodEnum.unmark: PortalChangeLogAction.unmarked,
        PortalMethodEnum.stabilize: PortalChangeLogAction.stabilize
    }

    def __init__(
            self,
            portal_repository: PortalRepository,
            portal_change_logs_service: PortalChangeLogsService
    ):
        self.__portal_repository = portal_repository
        self.__logs_service = portal_change_logs_service

    async def get_summary(self) -> PortalsSummary:
        summary = await self.__portal_repository.get_summary()
        return PortalsSummary(
            open=summary.open,
            closed=summary.closed,
            critical=summary.critical,
            prioritized_portals=_portals_to_short_info_portals(
                summary.prioritized_portals
            )
        )

    async def get_portals(self, offset: int = 0, limit: int = 10) -> list[ShortPortalInfo]:
        portals = await self.__portal_repository.get_list(offset, limit)
        return _portals_to_short_info_portals(portals)

    async def get_portal(self, portal_id: int) -> PortalInfo:
        portal = await self.__get_portal(portal_id)
        return PortalInfo(
            id=portal.id,
            name=portal.name,
            status=portal.status,
            energy=portal.energy.value,
            stability=portal.stability.value,
            world_destination=portal.world_destination,

            risk=_get_risk_info(portal),
            observers=portal.count_observers,
            expired=portal.expired,
            expired_at=portal.expires_at.value,
            marked=portal.marked,
        )

    async def get_best_action(self, portal_id: int) -> PortalActionEnum:
        return (await self.__get_portal(portal_id)).get_best_action()

    async def open(self, portal_id: int) -> UpdatedPortal:
        return await self.__change(portal_id, PortalMethodEnum.open)

    async def close(self, portal_id: int) -> UpdatedPortal:
        return await self.__change(portal_id, PortalMethodEnum.close)

    async def stabilize(self, portal_id: int) -> UpdatedPortal:
        return await self.__change(portal_id, PortalMethodEnum.stabilize)

    async def add_observer(self, portal_id: int) -> UpdatedPortal:
        return await self.__change(portal_id, PortalMethodEnum.add_observer)

    async def take_observer(self, portal_id: int) -> UpdatedPortal:
        return await self.__change(portal_id, PortalMethodEnum.take_observer)

    async def mark(self, portal_id: int) -> UpdatedPortal:
        try:
            return await self.__change(portal_id, PortalMethodEnum.mark)
        except UpdateToSameValueError as e:
            raise PortalIsAlreadyMarkedError from e

    async def unmark(self, portal_id: int) -> UpdatedPortal:
        try:
            return await self.__change(portal_id, PortalMethodEnum.unmark)
        except UpdateToSameValueError as e:
            raise PortalIsNotMarkedError from e

    async def __get_portal(self, portal_id: int) -> Portal:
        portal = await self.__portal_repository.get_by_id(portal_id)
        if portal is None:
            raise PortalNotFoundError(f"Portal with id {portal_id} was not found")
        return portal

    async def __change(self, portal_id: int, method: PortalMethodEnum) -> UpdatedPortal:
        portal = await self.__get_portal(portal_id)
        portal.do_method(method)
        await self.__portal_repository.save(portal)

        change_log_action = self.CHANGE_LOG_ACTIONS[method]
        change_log = await self.__logs_service.create_log(portal_id=portal_id, action=change_log_action)
        return UpdatedPortal(
            portal=PortalInfo(
                id=portal.id,
                name=portal.name,
                world_destination=portal.world_destination,
                energy=portal.energy.value,
                expired=portal.expired,
                expired_at=portal.expires_at.value,
                observers=portal.count_observers,
                risk=_get_risk_info(portal),
                stability=portal.stability.value,
                status=portal.status,
                marked=portal.marked,
            ),
            change_log=change_log
        )
