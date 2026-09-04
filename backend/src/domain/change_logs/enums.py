from enum import Enum


class PortalChangeLogAction(str, Enum):
    opened = 'opened'
    closed = 'closed'

    marked = 'marked'
    unmarked = 'unmarked'

    added_observer = 'added_observer'
    taken_observer = 'taken_observer'

    stabilize = 'stabilize'
