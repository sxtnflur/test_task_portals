from domain.common.errors import DomainError


class ServiceError(DomainError):
    pass


class NotFoundError(ServiceError, LookupError):
    pass
