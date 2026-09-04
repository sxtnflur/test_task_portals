from enum import  StrEnum


class PortalStatusEnum(StrEnum):
    open = 'open'
    closed = 'closed'


class PortalActionEnum(StrEnum):
    open = 'open'
    close = 'close'
    mark = 'mark'
    stabilize = 'stabilize'
    add_observers = 'add_observers'
    take_observers = 'take_observers'


class PortalMethodEnum(StrEnum):
    open = 'open'
    close = 'close'
    mark = 'mark'
    unmark = 'unmark'
    add_observer = 'add_observer'
    take_observer = 'take_observer'
    stabilize = 'stabilize'
