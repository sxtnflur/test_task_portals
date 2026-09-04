from dataclasses import dataclass
from typing import Any

from domain.common.errors import DomainWrongComparisonTypeError
from typing_extensions import Self


@dataclass
class Entity:
    id: Any

    comparison_field: str = 'id'

    def __eq__(self, other):
        return (
            isinstance(self, type(other)) and
            getattr(self, self.comparison_field) == getattr(other, self.comparison_field)
        )

    def __validate_supported_comparison(self, other, operand):
        if not isinstance(other, type(self)):
            raise DomainWrongComparisonTypeError(type(self), type(other), operand)

    def __ge__(self, other: Self):
        self.__validate_supported_comparison(other, '>=')
        return getattr(self, self.comparison_field) >= getattr(other, self.comparison_field)

    def __gt__(self, other: Self):
        self.__validate_supported_comparison(other, '>')
        return getattr(self, self.comparison_field) > getattr(other, self.comparison_field)

    def __le__(self, other: Self):
        self.__validate_supported_comparison(other, '<=')
        return getattr(self, self.comparison_field) <= getattr(other, self.comparison_field)

    def __lt__(self, other: Self):
        self.__validate_supported_comparison(other, '<')
        return getattr(self, self.comparison_field) < getattr(other, self.comparison_field)

    def __str__(self):
        return f'{type(self).__name__}({self.id!r})'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.id)
