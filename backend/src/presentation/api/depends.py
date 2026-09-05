from typing import Annotated

from config.settings import settings
from db import session_factory
from fastapi import Depends

from application.portal.service import PortalService
from application.change_logs.service import PortalChangeLogsService

from domain.portal.repositories import PortalRepository
from domain.change_logs.repositories import PortalChangeLogsRepository
from infra.repositories.postgres import PostgresPortalChangeLogsRepository, PostgresPortalRepository
from infra.db.base import create_engine, session_scope, create_session_factory
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session():
    async with session_scope(session_factory) as scope:
        yield scope


DbSessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


# REPOSITORIES
def get_portal_repository(session: DbSessionDependency):
    return PostgresPortalRepository(session)


PortalRepositoryDependency = Annotated[
    PortalRepository, Depends(get_portal_repository)
]


def get_portal_change_logs_repository(session: DbSessionDependency) -> PortalChangeLogsRepository:
    return PostgresPortalChangeLogsRepository(session)


PortalChangeLogsRepositoryDependency = Annotated[
    PortalChangeLogsRepository, Depends(get_portal_change_logs_repository)
]


def get_portal_change_logs_service(
    repository: PortalChangeLogsRepositoryDependency
):
    return PortalChangeLogsService(
        logs_repo=repository
    )


PortalChangeLogsServiceDependency = Annotated[PortalChangeLogsService, Depends(get_portal_change_logs_service)]


def get_portal_service(
        repository: PortalRepositoryDependency,
        portal_change_logs_service: PortalChangeLogsServiceDependency
) -> PortalService:
    return PortalService(
        portal_repository=repository,
        portal_change_logs_service=portal_change_logs_service
    )


PortalServiceDependency = Annotated[PortalService, Depends(get_portal_service)]
