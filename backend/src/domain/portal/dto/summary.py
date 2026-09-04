from dataclasses import dataclass

from domain.portal import Portal


@dataclass
class PortalsSummary:
    open: int
    closed: int
    critical: int
    prioritized_portals: list[Portal]
