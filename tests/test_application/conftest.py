import pytest

from application import PortalService
from application.change_logs import PortalChangeLogsService
from domain.change_logs import PortalChangeLog
from domain.change_logs import PortalChangeLogsRepository
from domain.portal.dto.summary import PortalsSummary
from domain.portal.entities import Portal
from domain.portal.repositories import PortalRepository


class FakePortalRepository(PortalRepository):
    """In-memory `PortalRepository` for application-layer unit tests."""

    def __init__(self, portals=()):
        self._portals = {portal.id: portal for portal in portals}
        self.saved: list[Portal] = []

    def seed(self, *portals: Portal) -> None:
        for portal in portals:
            self._portals[portal.id] = portal

    async def get_by_id(self, portal_id: int) -> Portal | None:
        return self._portals.get(portal_id)

    async def get_list(self, offset: int, limit: int) -> list[Portal]:
        return list(self._portals.values())[offset:offset + limit]

    async def add(self, portal: Portal) -> None:
        self._portals[portal.id] = portal

    async def save(self, portal: Portal) -> None:
        self._portals[portal.id] = portal
        self.saved.append(portal)

    async def get_summary(self) -> PortalsSummary:
        open_portals = [portal for portal in self._portals.values() if portal.is_open]
        closed_count = sum(1 for portal in self._portals.values() if portal.is_closed)

        risks = [(portal, portal.get_risk()) for portal in open_portals]
        critical = sorted(
            (pair for pair in risks if pair[1].high),
            key=lambda pair: pair[1].value,
            reverse=True,
        )

        return PortalsSummary(
            open=len(open_portals),
            closed=closed_count,
            critical=len(critical),
            prioritized_portals=[portal for portal, _ in critical],
        )


class FakePortalChangeLogsRepository(PortalChangeLogsRepository):
    """In-memory `PortalChangeLogsRepository` for application-layer unit tests."""

    def __init__(self):
        self.logs: list[PortalChangeLog] = []

    async def add(self, log: PortalChangeLog) -> None:
        self.logs.append(log)

    async def get_list(self, offset: int = 0, limit: int = 10, desc: bool = True) -> list[PortalChangeLog]:
        logs = sorted(self.logs, reverse=desc)
        return logs[offset:offset + limit]


@pytest.fixture
def portal_repository() -> FakePortalRepository:
    return FakePortalRepository()


@pytest.fixture
def change_logs_repository() -> FakePortalChangeLogsRepository:
    return FakePortalChangeLogsRepository()


@pytest.fixture
def change_logs_service(change_logs_repository) -> PortalChangeLogsService:
    return PortalChangeLogsService(change_logs_repository)


@pytest.fixture
def portal_service(portal_repository, change_logs_service) -> PortalService:
    return PortalService(portal_repository, change_logs_service)
