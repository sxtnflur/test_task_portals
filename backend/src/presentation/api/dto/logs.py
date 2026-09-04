import datetime
import uuid

from presentation.api.dto.common import ListResponse
from pydantic import BaseModel, ConfigDict

from domain.change_logs.enums import PortalChangeLogAction


class PortalChangeLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    portal_id: int
    action: PortalChangeLogAction
    acted_at: datetime.datetime
    detail: str | None = None


PortalLogsResponse = ListResponse[PortalChangeLog]
