"""Repository abstraction implemented by this package's adapters, plus the
shared plumbing every Postgres adapter needs.

`PortalRepository`/`PortalChangeLogsRepository` are re-exported here so
modules in this package import their port from one local place; concrete
repositories additionally inherit `BasePostgresRepository` for the
session they operate on.
"""
from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from domain.change_logs.repositories import PortalChangeLogsRepository
from domain.portal.repositories import PortalRepository

__all__ = ["PortalRepository", "PortalChangeLogsRepository", "BasePostgresRepository"]


class BasePostgresRepository(ABC):
    """Shared plumbing for Postgres-backed repository adapters.

    Takes an `AsyncSession` rather than owning an engine or a transaction:
    the caller (a request-scoped session, `infra.db.session_scope`, ...)
    controls the unit of work and commits it. Concrete repositories only
    `flush()` their own changes.

    Combine with the matching domain port, e.g.
    `class PostgresPortalRepository(BasePostgresRepository, PortalRepository)`.
    """

    def __init__(self, session: AsyncSession):
        self._session = session
