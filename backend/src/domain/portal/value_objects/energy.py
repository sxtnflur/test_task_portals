from domain.common.errors import ValueObjectValueError, DomainValueError
from domain.portal.errors import TooLargeValueError, TooSmallValueError
from domain.common.value_object import ValueObject


class Energy(ValueObject):
    max_value: int = 10

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise ValueObjectValueError(self, int)

        if value < 0:
            raise TooSmallValueError(f'Energy cannot be less than 0')
        if value > self.max_value:
            raise TooLargeValueError(f'Energy cannot be more than {self.max_value}')

        super().__init__(value)

    def is_high(self) -> bool:
        """Whether the energy level is high enough to be a risk factor on its own."""
        return self.value >= 7
