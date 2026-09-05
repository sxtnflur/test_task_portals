from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models in this package.

    Kept separate from the domain layer on purpose: domain entities
    (`Portal`, `PortalChangeLog`) know nothing about SQLAlchemy. Repositories
    below translate between ORM rows and domain aggregates.
    """


def create_engine(database_url: str | None = None) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def create_all_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def session_scope(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    """Open a session bound to one unit of work: commit on success, roll back on error.

    Repositories only `flush()` their own changes; committing (and thus
    fixing the transaction boundary) is this context manager's job, so a
    caller can group several repository calls into a single atomic unit
    of work:

        async with session_scope(session_factory) as session:
            await PostgresPortalRepository(session).save(portal)
            await PostgresPortalChangeLogsRepository(session).add(log)
    """
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
