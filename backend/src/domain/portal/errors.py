from domain.common.errors import DomainValueError, DomainError


class InvalidPortalMethodError(DomainValueError):
    def __init__(self, method):
        super().__init__(f'{method!r} is not existing method for portal')


class ClosedPortalError(DomainValueError):
    def __init__(self):
        super().__init__('Portal is closed')


class TooHighRiskError(DomainError):
    def __init__(self):
        super().__init__('Too high risk level')


class TooLargeValueError(DomainValueError):
    def __init__(self, detail: str):
        super().__init__('Too large value: ' + detail)


class TooSmallValueError(DomainValueError):
    def __init__(self, detail: str):
        super().__init__('Too small value: ' + detail)

