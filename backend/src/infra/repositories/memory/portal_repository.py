from typing import Iterable

from domain.portal.dto.summary import PortalsSummary
from domain.portal.entities.portal import Portal

from infra.repositories.memory.base import PortalRepository


class MemoryPortalRepository(PortalRepository):
    def __init__(self, portals: Iterable[Portal] = ()):
        self.portals = {portal.id: portal for portal in portals}
        self.saved = []

    async def get_by_id(self, portal_id: int) -> Portal | None:
        return self.portals.get(portal_id)

    async def get_list(self, offset: int, limit: int) -> list[Portal]:
        if offset > len(self.portals):
            return []
        if limit > len(self.portals):
            res = list(self.portals.values())[offset:]
        else:
            res = list(self.portals.values())[offset:limit]
        res.reverse()
        return res

    async def add(self, portal: Portal) -> None:
        self.portals[portal.id] = portal

    async def save(self, portal: Portal) -> None:
        self.portals[portal.id] = portal
        self.saved.append(portal)

    async def get_summary(self) -> PortalsSummary:
        open_portals = [portal for portal in self.portals.values() if portal.is_open]
        closed_count = sum(1 for portal in self.portals.values() if portal.is_closed)

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
