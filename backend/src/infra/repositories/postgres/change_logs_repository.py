from sqlalchemy import select

from domain.change_logs.entity import PortalChangeLog
from domain.change_logs.enums import PortalChangeLogAction

from infra.db.models import PortalChangeLogModel
from infra.repositories.postgres.base import BasePostgresRepository, PortalChangeLogsRepository


def _row_to_change_log(row: PortalChangeLogModel) -> PortalChangeLog:
    return PortalChangeLog(
        log_id=row.id,
        portal_id=row.portal_id,
        action=PortalChangeLogAction(row.action),
        detail=row.detail,
        acted_at=row.acted_at,
    )


class PostgresPortalChangeLogsRepository(BasePostgresRepository, PortalChangeLogsRepository):
    """`PortalChangeLogsRepository` backed by a Postgres table via SQLAlchemy."""

    async def get_list(self, offset: int = 0, limit: int = 10, desc: bool = True) -> list[PortalChangeLog]:
        order = PortalChangeLogModel.acted_at.desc() if desc else PortalChangeLogModel.acted_at.asc()
        statement = (
            select(PortalChangeLogModel)
            .order_by(order)
            .offset(offset)
            .limit(limit)
        )
        rows = await self._session.scalars(statement)
        return [_row_to_change_log(row) for row in rows]

    async def add(self, log: PortalChangeLog) -> None:
        self._session.add(PortalChangeLogModel(
            id=log.id,
            portal_id=log.portal_id,
            action=log.action.value,
            detail=log.detail,
            acted_at=log.acted_at,
        ))
        await self._session.flush()
