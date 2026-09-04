from sqlalchemy import func, select

from domain.portal.dto.summary import PortalsSummary
from domain.portal.entities.portal import Portal
from domain.portal.enums import PortalStatusEnum
from domain.portal.value_objects.energy import Energy
from domain.portal.value_objects.expires_at import ExpiresAt
from domain.portal.value_objects.stability import PortalStability

from infra.db.models import PortalModel
from infra.repositories.postgres.base import BasePostgresRepository, PortalRepository


def _portal_to_row_values(portal: Portal) -> dict:
    return dict(
        id=portal.id,
        name=portal.name,
        world_destination=portal.world_destination,
        energy=portal.energy.value,
        stability=portal.stability.value,
        expires_at=portal.expires_at.value,
        status=portal.status.value,
        count_observers=portal.count_observers,
        marked=portal.marked,
    )


def _row_to_portal(row: PortalModel) -> Portal:
    return Portal(
        portal_id=row.id,
        name=row.name,
        world_destination=row.world_destination,
        energy=Energy(row.energy),
        stability=PortalStability(row.stability),
        expires_at=ExpiresAt(row.expires_at),
        status=PortalStatusEnum(row.status),
        count_observers=row.count_observers,
        marked=row.marked,
    )


class PostgresPortalRepository(BasePostgresRepository, PortalRepository):
    """`PortalRepository` backed by a Postgres `portals` table via SQLAlchemy."""

    async def get_by_id(self, portal_id: int) -> Portal | None:
        row = await self._session.get(PortalModel, portal_id)
        return _row_to_portal(row) if row is not None else None

    async def get_list(self, offset: int, limit: int) -> list[Portal]:
        statement = (
            select(PortalModel)
            .order_by(PortalModel.id.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = await self._session.scalars(statement)
        return [_row_to_portal(row) for row in rows]

    async def add(self, portal: Portal) -> None:
        self._session.add(PortalModel(**_portal_to_row_values(portal)))
        await self._session.flush()

    async def save(self, portal: Portal) -> None:
        row = await self._session.get(PortalModel, portal.id)
        if row is None:
            raise LookupError(f"Portal with id {portal.id} does not exist")

        for column, value in _portal_to_row_values(portal).items():
            setattr(row, column, value)

        await self._session.flush()

    async def get_summary(self) -> PortalsSummary:
        # Risk is derived domain logic (stability/energy/expiry, re-evaluated
        # against the current time), not a stored column, so it can't be
        # filtered in SQL without duplicating that logic there. Only closed
        # portals are irrelevant to it, so we let the database do what it's
        # good at (counting) and only pull rows - and compute risk - for the
        # open ones.
        open_rows = await self._session.scalars(
            select(PortalModel)
            .where(PortalModel.status == PortalStatusEnum.open.value)
        )
        # A row stored as `status='open'` can still reconstruct as a closed
        # `Portal`: `Portal.__init__` re-derives `closed` from an already-past
        # `expires_at` regardless of the stored column (the row is simply
        # stale until something calls `close()` on it) - `get_risk()` then
        # returns `None` for it, so it must be excluded here too.
        candidates = [_row_to_portal(row) for row in open_rows]
        open_portals = [portal for portal in candidates if portal.is_open]
        naturally_expired_count = len(candidates) - len(open_portals)

        closed_count = await self._session.scalar(
            select(func.count())
            .select_from(PortalModel)
            .where(PortalModel.status == PortalStatusEnum.closed.value)
        )
        closed_count += naturally_expired_count

        risks = [(portal, portal.get_risk()) for portal in open_portals]
        critical = sorted(
            (pair for pair in risks if pair[1].high),
            key=lambda pair: pair[1].value,
            reverse=True,
        )

        return PortalsSummary(
            open=len(open_portals),
            closed=closed_count,
            critical=len(critical),
            prioritized_portals=[portal for portal, _ in critical],
        )
