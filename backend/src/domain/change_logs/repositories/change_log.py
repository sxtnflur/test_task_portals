from abc import ABC, abstractmethod

from domain.change_logs.entity import PortalChangeLog


class PortalChangeLogsRepository(ABC):
    @abstractmethod
    async def get_list(self, offset: int = 0, limit: int = 10, desc: bool = True) -> list[PortalChangeLog]:
        """Returns list of portal change logs orderd by 'acted_at'"""
        raise NotImplementedError

    @abstractmethod
    async def add(self, log: PortalChangeLog) -> None:
        """Add a new portal change log."""
        raise NotImplementedError
