from domain.common.errors import DomainWrongComparisonTypeError, DomainUnsupportedOperandTypeError


class ValueObject:
    def __init__(self, value):
        if isinstance(value, type(self)):
            value = value.value

        self.__value = value

    @property
    def value(self):
        return self.__value

    def __str__(self):
        return f'{type(self).__name__}({self.value})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.value == other.value

        if isinstance(other, type(self.value)):
            return self.value == other

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.value < other.value

        if isinstance(other, type(self.value)):
            return self.value < other

        raise DomainWrongComparisonTypeError(type(self), type(other), '<')

    def __le__(self, other):
        if isinstance(other, type(self)):
            return self.value <= other.value

        if isinstance(other, type(self.value)):
            return self.value <= other

        raise DomainWrongComparisonTypeError(type(self), type(other), '<=')

    def __gt__(self, other):
        if isinstance(other, type(self)):
            return self.value > other.value

        if isinstance(other, type(self.value)):
            return self.value > other

        raise DomainWrongComparisonTypeError(type(self), type(other), '>')

    def __ge__(self, other):
        if isinstance(other, type(self)):
            return self.value >= other.value

        if isinstance(other, type(self.value)):
            return self.value >= other

        raise DomainWrongComparisonTypeError(type(self), type(other), '>=')

    def __add__(self, other):
        if isinstance(other, type(self)):
            return type(self)(self.value + other.value)

        if isinstance(other, type(self.value)):
            return type(self)(self.value + other)

        raise DomainUnsupportedOperandTypeError(type(self), type(other), '+')

    def __sub__(self, other):
        if isinstance(other, type(self)):
            return type(self)(self.value - other.value)

        if isinstance(other, type(self.value)):
            return type(self)(self.value - other)

        raise DomainUnsupportedOperandTypeError(type(self), type(other), '-')

    def __radd__(self, other):
        if isinstance(other, type(self)):
            return type(self)(other.value + self.value)

        if isinstance(other, type(self.value)):
            return type(self)(other + self.value)

        raise DomainUnsupportedOperandTypeError(type(other), type(self), '+=')

    def __rsub__(self, other):
        print(f"{type(self.value)=} {type(other)=}")
        if isinstance(other, type(self)):
            return type(self)(other.value - self.value)

        if isinstance(other, type(self.value)):
            return type(self)(other - self.value)

        raise DomainUnsupportedOperandTypeError(type(other), type(self), '-=')

    def __hash__(self):
        return hash(self.__value)
