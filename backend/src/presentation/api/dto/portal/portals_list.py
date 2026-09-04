import datetime
from pydantic import BaseModel, ConfigDict, Field

from domain.risk.enums import RiskLevel
from domain.portal.enums import PortalStatusEnum
from presentation.api.dto.common import ListResponse


class PortalShortInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    world_destination: str
    energy: int
    stability: float
    expired_at: datetime.datetime = Field(description='Timestamp when the portal collapses')
    expired: bool
    observers: int
    status: PortalStatusEnum
    risk_level: RiskLevel | None = Field(description='null when the portal is expired')
    marked: bool


PortalsListResponse = ListResponse[PortalShortInfo]
