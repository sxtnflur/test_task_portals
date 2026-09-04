from abc import ABC, abstractmethod

from domain.portal.dto.summary import PortalsSummary
from domain.portal.entities.portal import Portal


class PortalRepository(ABC):
    """Port for storing and retrieving Portal aggregate roots.

    Concrete implementations belong to the infrastructure layer.
    """

    @abstractmethod
    async def get_by_id(self, portal_id: int) -> Portal | None:
        """Return a portal by id, or None if it does not exist."""
        raise NotImplementedError

    @abstractmethod
    async def get_list(self, offset: int, limit: int) -> list[Portal]:
        """Returns list of portals ordered by id DESC"""
        raise NotImplementedError

    @abstractmethod
    async def add(self, portal: Portal) -> None:
        """Add a new portal aggregate."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, portal: Portal) -> None:
        """Persist changes made to an existing portal aggregate."""
        raise NotImplementedError

    @abstractmethod
    async def get_summary(self) -> PortalsSummary:
        raise NotImplementedError
