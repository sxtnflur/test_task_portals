import datetime
import logging
import uuid

from domain.common.entity import Entity
from domain.change_logs.enums import PortalChangeLogAction


class PortalChangeLog(Entity):
    comparison_field = 'acted_at'

    def __init__(
        self,
        log_id: uuid.UUID,
        portal_id: int,
        action: PortalChangeLogAction,
        detail: str | None = None,
        acted_at: datetime.datetime | None = None
    ):
        self.__id = log_id
        self.__portal_id = portal_id
        self.__action = action
        self.__detail = detail
        self.__acted_at = acted_at or datetime.datetime.utcnow()

    @classmethod
    def create(
            cls,
            portal_id: int,
            action: PortalChangeLogAction,
            detail: str | None = None,
            acted_at: datetime.datetime | None = None
    ):
        return cls(
            log_id=uuid.uuid4(),
            portal_id=portal_id,
            action=action,
            detail=detail,
            acted_at=acted_at
        )

    def __hash__(self):
        return hash(self.__id)

    @property
    def id(self):
        return self.__id

    @property
    def portal_id(self):
        return self.__portal_id

    @property
    def action(self):
        return self.__action

    @property
    def detail(self):
        return self.__detail

    @property
    def acted_at(self):
        return self.__acted_at

    def __str__(self):
        return (
            f'Portal #{self.__portal_id} got action {self.__action.name!r} '
            f'at {self.__acted_at.strftime("%d.%m.%Y %H:%M")}'
        ) + (f': ({self.__detail})' if self.__detail else '')

    def __repr__(self):
        return f'{type(self).__name__} #{self.__id} ({self})'

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action.value,
            'portal_id': self.portal_id,
            'acted_at': self.acted_at,
            'detail': self.detail
        }

    @property
    def log_text(self):
        return self.__str__()

    def log(self, logger: logging.Logger | None = None):
        if logger is None:
            logger = logging.getLogger("Portal Chage Log")
        logger.info(self.log_text)
