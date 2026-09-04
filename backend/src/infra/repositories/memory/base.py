"""Repository abstraction implemented by this package's adapters.

Re-exported here so every module in this package imports its port from one
local place (`from .base import PortalRepository`) instead of reaching into
`domain` directly.
"""
from abc import ABC

from domain.change_logs.repositories import PortalChangeLogsRepository
from domain.portal.repositories import PortalRepository

__all__ = ["PortalRepository", "PortalChangeLogsRepository"]


class BaseMemoryRepository(ABC):
    pass
