from application.errors import NotFoundError, ServiceError
from domain.common.errors import UpdateToSameValueError


class PortalNotFoundError(NotFoundError):
    pass


class PortalIsAlreadyMarkedError(UpdateToSameValueError, ServiceError):
    def __init__(self):
        self.message = 'Portal is already marked'


class PortalIsNotMarkedError(UpdateToSameValueError, ServiceError):
    def __init__(self):
        self.message = 'Portal is not marked, so you cannot unmark it'
