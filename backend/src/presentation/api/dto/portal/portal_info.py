from pydantic import BaseModel, ConfigDict, Field

from domain.portal.enums import PortalActionEnum
from domain.risk.enums import RiskFactorEnum
from presentation.api.dto.portal import PortalShortInfo
from presentation.api.dto.logs import PortalLogsResponse


class RiskFactor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: RiskFactorEnum
    value: float = Field(ge=0, le=1)


class UpdatedPortalResponse(PortalShortInfo):
    risk_value: int | None = Field(ge=0, le=10)
    risk_factors: list[RiskFactor] | None = Field(default_factory=list)
    recommended_action: PortalActionEnum


class FullPortalInfoResponse(UpdatedPortalResponse):
    change_logs: PortalLogsResponse
