from typing import TYPE_CHECKING

from typing_extensions import Literal

if TYPE_CHECKING:
    # `value_object.py` imports error classes from this module at runtime
    # (for its own `__lt__`/`__add__`/... methods) - importing `ValueObject`
    # back here at runtime would make the two modules circularly import each
    # other. This name is only ever used in a type hint below, so it only
    # needs to exist for type checkers, not at runtime.
    from domain.common.value_object import ValueObject


class DomainError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return f'{type(self).__name__}({self.message})'


class DomainValueError(DomainError, ValueError):
    pass


class ValueObjectValueError(DomainError):
    def __init__(self, vo: 'ValueObject', type_: type, /):
        self.message = f"{type(vo).__name__}`s value can be only {type_}"


class DomainTypeError(DomainError):
    pass


class DomainUnsupportedOperandTypeError(DomainError):
    def __init__(self, a: type, b: type, operand: Literal['+', '+=', '-', '-=']):
        super().__init__(
            f"unsupported operand type(s) for {operand}: '{a.__name__}' and '{b.__name__}'"
        )


class DomainWrongComparisonTypeError(DomainError):
    def __init__(self, a: type, b: type, operator: Literal['<', '>', '<=', '>=']):
        super().__init__(
            f"'{operator}' not supported between instances of '{a}' and '{b}'"
        )


class UpdateToSameValueError(DomainValueError):
    def __init__(self, obj, field, value):
        super().__init__(f'{obj!r}`s field {field!r} is already {value!r}')
