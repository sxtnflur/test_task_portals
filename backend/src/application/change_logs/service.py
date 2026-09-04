import datetime

from domain.change_logs.entity import PortalChangeLog, PortalChangeLogAction
from domain.change_logs.repositories import PortalChangeLogsRepository


class PortalChangeLogsService:
    def __init__(self, logs_repo: PortalChangeLogsRepository):
        self.__logs_repo = logs_repo

    async def create_log(
        self,
        portal_id: int,
        action: PortalChangeLogAction,
        detail: str | None = None,
        acted_at: datetime.datetime | None = None
    ) -> PortalChangeLog:
        log = PortalChangeLog.create(
            portal_id=portal_id,
            action=action,
            detail=detail,
            acted_at=acted_at
        )
        await self.__logs_repo.add(log)
        return log

    async def get_list(self, offset: int = 0, limit: int = 10) -> list[PortalChangeLog]:
        return await self.__logs_repo.get_list(offset, limit)
