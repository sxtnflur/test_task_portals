import datetime
import math

from domain.common.value_object import ValueObject
from domain.common.errors import ValueObjectValueError, DomainUnsupportedOperandTypeError


class ExpiresAt(ValueObject):
    CLOSING_SOON_WINDOW = datetime.timedelta(seconds=60)
    """Remaining time at which `urgency` crosses 0.5, the closing-soon
    threshold. Chosen so 2 minutes left reads as normal (urgency 0.25) and
    30 seconds left already reads as closing soon (urgency ~0.71)."""

    _URGENCY_DECAY_SECONDS = CLOSING_SOON_WINDOW.total_seconds() / math.log(2)

    def __init__(self, value: datetime.datetime):
        if not isinstance(value, datetime.datetime):
            raise ValueObjectValueError(self, datetime.datetime)

        super().__init__(value)

    @property
    def expires_in(self):
        return self.value - datetime.datetime.utcnow()

    @property
    def expires_in_minutes(self):
        return max(self.expires_in.total_seconds() / 60, 0)

    @property
    def expired(self):
        return self.value <= datetime.datetime.utcnow()

    @property
    def urgency(self) -> float:
        """
        :return: Float: 1 - now, 0 - well before expiry. Crosses 0.5 exactly
        at `CLOSING_SOON_WINDOW` remaining.
        """
        seconds_left = max(self.expires_in.total_seconds(), 0)
        return math.exp(-seconds_left / self._URGENCY_DECAY_SECONDS)

    def is_closing_soon(self) -> bool:
        """Whether the portal is close enough to expiry to be a risk factor."""
        return self.urgency >= 0.5

    @classmethod
    def now(cls):
        return cls(datetime.datetime.utcnow())

    def __add__(self, other):
        if isinstance(other, datetime.timedelta):
            return type(self)(self.value + other)
        raise DomainUnsupportedOperandTypeError(type(self), type(other), '+')

    def __radd__(self, other):
        if isinstance(other, datetime.timedelta):
            return type(self)(self.value + other)
        raise DomainUnsupportedOperandTypeError(type(self), type(other), '+=')

    def __sub__(self, other):
        if isinstance(other, datetime.timedelta):
            return type(self)(self.value - other)
        raise DomainUnsupportedOperandTypeError(type(self), type(other), '-')

    def __rsub__(self, other):
        if isinstance(other, datetime.timedelta):
            return type(self)(self.value - other)
        raise DomainUnsupportedOperandTypeError(type(self), type(other), '-=')