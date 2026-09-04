from presentation.api.depends import PortalChangeLogsServiceDependency

from fastapi import APIRouter
from presentation.api.dto.common import SuccessResponse
from presentation.api.dto.logs import PortalChangeLog, PortalLogsResponse

router = APIRouter(prefix='/logs', tags=['logs'])


@router.get('/portal')
async def get_list_portal_logs(
    service: PortalChangeLogsServiceDependency,
    offset: int = 0,
    limit: int = 10
) -> SuccessResponse[PortalLogsResponse]:
    logs = await service.get_list(
        offset=offset, limit=limit
    )
    response = PortalLogsResponse(
        result=list(map(PortalChangeLog.model_validate, logs)),
        offset=offset, limit=limit
    )
    return SuccessResponse[PortalLogsResponse](response)
