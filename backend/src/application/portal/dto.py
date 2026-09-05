import datetime
from dataclasses import dataclass

from domain.portal.enums import PortalActionEnum, PortalStatusEnum
from domain.risk.enums import RiskLevel
from domain.risk.risk_factor import RiskFactor
from domain.change_logs.entity import PortalChangeLog


@dataclass
class RiskInfo:
    level: RiskLevel | None
    """`None` when the portal is closed - risk cannot be assessed for it."""
    value: int
    factors: tuple[RiskFactor]
    recommended_action: PortalActionEnum


@dataclass
class ShortPortalInfo:
    id: int
    name: str
    world_destination: str
    expired_at: datetime.datetime
    expired: bool
    status: PortalStatusEnum
    observers: int
    energy: int
    stability: float
    risk_level: RiskLevel | None
    """`None` when the portal is expired - risk cannot be assessed for it."""
    marked: bool


@dataclass
class PortalInfo:
    id: int
    name: str
    world_destination: str
    expired_at: datetime.datetime
    expired: bool
    status: PortalStatusEnum
    observers: int

    energy: int
    stability: float
    risk: RiskInfo
    marked: bool


@dataclass
class UpdatedPortal:
    portal: PortalInfo
    change_log: PortalChangeLog


@dataclass
class PortalsSummary:
    open: int
    closed: int
    critical: int
    prioritized_portals: list[ShortPortalInfo]
