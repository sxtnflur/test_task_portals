from typing import Literal

from domain.common.value_object import ValueObject
from domain.common.errors import ValueObjectValueError, DomainValueError
from domain.portal.errors import TooSmallValueError, TooLargeValueError


class PortalStability(ValueObject):
    min_value = 0.0
    max_value = 10

    def __init__(self, value: float):
        if isinstance(value, int):
            value = float(value)

        if not isinstance(value, float):
            raise ValueObjectValueError(self, float)

        if value < 0:
            raise TooSmallValueError(f'Stability cannot be less than 0')

        if value > self.max_value:
            raise TooLargeValueError(f'Stability cannot be more than {self.max_value}')

        super().__init__(value)

    def level(self) -> Literal["critical", "middle", "full"]:
        if self.is_full():
            return "full"
        if self.is_middle():
            return "middle"
        return "critical"

    def is_full(self) -> bool:
        return self.value == 10

    def is_middle(self) -> bool:
        return 5 < self.value < 10

    def is_critical(self) -> bool:
        return self.value <= 5
