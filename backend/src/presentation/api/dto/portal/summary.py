from pydantic import BaseModel

from presentation.api.dto.portal.portals_list import PortalShortInfo


class PortalsSummary(BaseModel):
    open: int
    closed: int
    critical: int
    prioritized_portals: list[PortalShortInfo]
