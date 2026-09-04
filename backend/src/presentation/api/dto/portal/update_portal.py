from pydantic import BaseModel

from domain.portal.enums import PortalActionEnum
from presentation.api.dto.portal.portal_info import UpdatedPortalResponse
from presentation.api.dto.logs import PortalChangeLog


class PortalActionResponseDTO(BaseModel):
    action: PortalActionEnum


class UpdatePortalResponse(BaseModel):
    portal: UpdatedPortalResponse
    change_log: PortalChangeLog
