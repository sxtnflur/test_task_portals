import datetime
import uuid

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.base import Base


class PortalModel(Base):
    """Row shape for a `Portal` aggregate.

    Enum fields (`status`) are stored as plain strings and converted
    explicitly in the repository, rather than relying on SQLAlchemy's
    `Enum` type (which persists the member *name*, not `.value` - a subtle
    mismatch trap if the two ever diverge). Plain strings keep the mapping
    explicit and boring.
    """

    __tablename__ = "portals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255))
    world_destination: Mapped[str] = mapped_column(String(255))
    energy: Mapped[int] = mapped_column(Integer)
    stability: Mapped[float] = mapped_column(Float)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False))
    status: Mapped[str] = mapped_column(String(16))
    count_observers: Mapped[int] = mapped_column(Integer, default=0)
    marked: Mapped[bool] = mapped_column(Boolean, default=False)


class PortalChangeLogModel(Base):
    """Row shape for a `PortalChangeLog` entry.

    No foreign key to `portals.id` on purpose: change logs are an
    append-only audit trail belonging to their own aggregate, not a detail
    table of `Portal` - it should keep recording history even if the portal
    it refers to is later removed.
    """

    __tablename__ = "portal_change_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    portal_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(50))
    detail: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    acted_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=False), index=True)
