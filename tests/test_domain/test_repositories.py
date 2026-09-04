import asyncio
from dataclasses import dataclass

import pytest

from domain.change_logs.repositories.change_log import PortalChangeLogsRepository
from domain.portal.dto.summary import PortalsSummary
from domain.portal.repositories.portal_repository import PortalRepository


@dataclass
class FakePortal:
    id: int


def test_portal_repository_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        PortalRepository()


def test_portal_repository_subclass_must_implement_all_abstract_methods():
    class Incomplete(PortalRepository):
        async def get_by_id(self, portal_id):
            return None

    with pytest.raises(TypeError):
        Incomplete()


def test_portal_repository_full_subclass_can_be_instantiated_and_used():
    class InMemory(PortalRepository):
        def __init__(self):
            self.items = {}

        async def get_by_id(self, portal_id):
            return self.items.get(portal_id)

        async def get_list(self, offset, limit):
            return list(self.items.values())[offset:offset + limit]

        async def add(self, portal):
            self.items[portal.id] = portal

        async def save(self, portal):
            self.items[portal.id] = portal

        async def get_summary(self):
            return PortalsSummary(open=0, closed=0, critical=0, prioritized_portals=[])

    async def scenario():
        repo = InMemory()
        portal = FakePortal(id=1)

        await repo.add(portal)

        assert await repo.get_by_id(1) is portal
        assert await repo.get_by_id(999) is None
        assert await repo.get_list(0, 10) == [portal]

    asyncio.run(scenario())


def test_change_logs_repository_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        PortalChangeLogsRepository()


def test_change_logs_repository_subclass_must_implement_all_abstract_methods():
    class Incomplete(PortalChangeLogsRepository):
        async def get_list(self, offset=0, limit=10, desc=True):
            return []

    with pytest.raises(TypeError):
        Incomplete()


def test_portal_repository_base_methods_raise_not_implemented():
    class PassThrough(PortalRepository):
        async def get_by_id(self, portal_id):
            return await super().get_by_id(portal_id)

        async def get_list(self, offset, limit):
            return await super().get_list(offset, limit)

        async def add(self, portal):
            return await super().add(portal)

        async def save(self, portal):
            return await super().save(portal)

        async def get_summary(self):
            return await super().get_summary()

    async def scenario():
        repo = PassThrough()
        for coro in (
            repo.get_by_id(1),
            repo.get_list(0, 10),
            repo.add(FakePortal(id=1)),
            repo.save(FakePortal(id=1)),
            repo.get_summary(),
        ):
            with pytest.raises(NotImplementedError):
                await coro

    asyncio.run(scenario())


def test_change_logs_repository_base_methods_raise_not_implemented():
    class PassThrough(PortalChangeLogsRepository):
        async def get_list(self, offset=0, limit=10, desc=True):
            return await super().get_list(offset, limit, desc)

        async def add(self, log):
            return await super().add(log)

    async def scenario():
        repo = PassThrough()
        with pytest.raises(NotImplementedError):
            await repo.get_list()
        with pytest.raises(NotImplementedError):
            await repo.add("fake-log")

    asyncio.run(scenario())
