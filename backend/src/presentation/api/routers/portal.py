from fastapi import APIRouter, status

from application.portal.dto import UpdatedPortal

from presentation.api.depends import PortalServiceDependency, PortalChangeLogsServiceDependency
from presentation.api.dto.common import SuccessResponse, EmptySuccessResponse
from presentation.api.dto.logs import PortalChangeLog, PortalLogsResponse
from presentation.api.dto.portal import (
    PortalActionResponseDTO,
    UpdatedPortalResponse, RiskFactor,
    PortalIdDTO, PortalShortInfo, PortalsListResponse,
    UpdatePortalResponse, FullPortalInfoResponse,
    PortalsSummary
)

router = APIRouter(prefix="/portals", tags=["portals"])


SuccessUpdatedResponse = SuccessResponse[UpdatePortalResponse]


def _updated_portal_to_response(updated_portal: UpdatedPortal) -> SuccessUpdatedResponse:
    portal_info = updated_portal.portal
    change_log = updated_portal.change_log
    return SuccessUpdatedResponse(
        UpdatePortalResponse(
            portal=UpdatedPortalResponse(
                id=portal_info.id,
                name=portal_info.name,
                world_destination=portal_info.world_destination,
                status=portal_info.status,
                energy=portal_info.energy,
                stability=portal_info.stability,
                expired_at=portal_info.expired_at,
                observers=portal_info.observers,
                expired=portal_info.expired,
                risk_level=portal_info.risk.level,
                risk_value=portal_info.risk.value,
                risk_factors=list(map(RiskFactor.model_validate, portal_info.risk.factors)),
                recommended_action=portal_info.risk.recommended_action,
                marked=portal_info.marked,
            ),
            change_log=PortalChangeLog(
                id=change_log.id,
                portal_id=change_log.portal_id,
                action=change_log.action,
                acted_at=change_log.acted_at,
                detail=change_log.detail
            )
        )
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[PortalsListResponse]
)
async def get_portals(
        portal_service: PortalServiceDependency,
        offset: int = 0,
        limit: int = 10
):
    portals = await portal_service.get_portals(offset, limit)

    response = PortalsListResponse(
        result=list(map(PortalShortInfo.model_validate, portals)),
        offset=offset, limit=limit
    )
    return SuccessResponse[PortalsListResponse](response)


@router.get(
    "/summary",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[PortalsSummary]
)
async def get_summary(
    service: PortalServiceDependency
):
    summary = await service.get_summary()
    response = PortalsSummary(
        open=summary.open,
        closed=summary.closed,
        critical=summary.critical,
        prioritized_portals=list(map(
            PortalShortInfo.model_validate,
            summary.prioritized_portals
        ))
    )
    return SuccessResponse[PortalsSummary](response)


@router.get(
    "/{portal_id}",
    response_model=SuccessResponse[FullPortalInfoResponse],
    status_code=status.HTTP_200_OK
)
async def get_portal_info(
        portal_id: int,
        portal_service: PortalServiceDependency,
        logs_service: PortalChangeLogsServiceDependency
):
    portal_info = await portal_service.get_portal(portal_id)

    offset, limit = 0, 10
    change_logs = await logs_service.get_list(offset=offset, limit=limit)
    response = FullPortalInfoResponse(
        id=portal_info.id,
        name=portal_info.name,
        world_destination=portal_info.world_destination,
        status=portal_info.status,
        energy=portal_info.energy,
        stability=portal_info.stability,
        expired_at=portal_info.expired_at,
        observers=portal_info.observers,
        expired=portal_info.expired,
        risk_level=portal_info.risk.level,
        risk_value=portal_info.risk.value,
        risk_factors=list(map(RiskFactor.model_validate, portal_info.risk.factors)),
        recommended_action=portal_info.risk.recommended_action,
        marked=portal_info.marked,
        change_logs=PortalLogsResponse(
            result=list(map(PortalChangeLog.model_validate, change_logs)),
            offset=offset, limit=limit
        )
    )
    return SuccessResponse[FullPortalInfoResponse](response)


@router.get(
    "/{portal_id}/recommendedAction",
    response_model=SuccessResponse[PortalActionResponseDTO],
    status_code=status.HTTP_200_OK
)
async def get_recommended_action(
        portal_id: int,
        service: PortalServiceDependency,
) -> SuccessResponse[PortalActionResponseDTO]:
    action = await service.get_best_action(portal_id)
    return SuccessResponse[PortalActionResponseDTO](
        PortalActionResponseDTO(action=action)
    )


@router.post("/open", status_code=status.HTTP_200_OK)
async def open_portal(
        request: PortalIdDTO,
        service: PortalServiceDependency,
) -> SuccessUpdatedResponse:
    updated = await service.open(request.portal_id)
    return _updated_portal_to_response(updated)


@router.post("/close", status_code=status.HTTP_200_OK)
async def close_portal(
        request: PortalIdDTO,
        service: PortalServiceDependency,
) -> SuccessUpdatedResponse:
    updated = await service.close(request.portal_id)
    return _updated_portal_to_response(updated)


@router.post("/stabilize", status_code=status.HTTP_200_OK)
async def stabilize_portal(
        request: PortalIdDTO,
        service: PortalServiceDependency,
) -> SuccessUpdatedResponse:
    updated = await service.stabilize(request.portal_id)
    return _updated_portal_to_response(updated)


@router.post("/observers/add", status_code=status.HTTP_200_OK)
async def add_observer(
        request: PortalIdDTO,
        service: PortalServiceDependency,
) -> SuccessUpdatedResponse:
    updated = await service.add_observer(request.portal_id)
    return _updated_portal_to_response(updated)


@router.post("/observers/take", status_code=status.HTTP_200_OK)
async def take_observer(
        request: PortalIdDTO,
        service: PortalServiceDependency,
) -> SuccessUpdatedResponse:
    updated = await service.take_observer(request.portal_id)
    return _updated_portal_to_response(updated)


@router.post("/mark", status_code=status.HTTP_200_OK)
async def mark_portal(
        request: PortalIdDTO,
        service: PortalServiceDependency
) -> SuccessUpdatedResponse:
    updated = await service.mark(request.portal_id)
    return _updated_portal_to_response(updated)


@router.post("/unmark", status_code=status.HTTP_200_OK)
async def unmark_portal(
        request: PortalIdDTO,
        service: PortalServiceDependency,
) -> SuccessUpdatedResponse:
    updated = await service.unmark(request.portal_id)
    return _updated_portal_to_response(updated)