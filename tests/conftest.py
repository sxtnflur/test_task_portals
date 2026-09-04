import datetime

import pytest

from domain.portal.entities import Portal
from domain.portal.value_objects import expires_at as expires_at_module
from domain.portal.value_objects.energy import Energy
from domain.portal.value_objects import ExpiresAt
from domain.portal.value_objects.stability import PortalStability


class Clock:
    """A controllable stand-in for `datetime.datetime.utcnow()`.

    The domain reads the current time directly (`datetime.datetime.utcnow()`)
    instead of receiving it as a dependency, so tests that need to move time
    forward (e.g. to make a portal expire after it was created) would
    otherwise have to `time.sleep`. This fixture patches the `datetime` class
    seen by `ExpiresAt` so time can be advanced instantly and deterministically.
    """

    def __init__(self, now: datetime.datetime):
        self.now = now

    def advance(self, **timedelta_kwargs):
        self.now += datetime.timedelta(**timedelta_kwargs)


@pytest.fixture
def clock(monkeypatch) -> Clock:
    class FrozenDatetime(datetime.datetime):
        @classmethod
        def utcnow(cls):
            return state.now

    monkeypatch.setattr(expires_at_module.datetime, "datetime", FrozenDatetime)

    # `state.now` must itself be a `FrozenDatetime` instance: datetime arithmetic
    # preserves the subclass (`FrozenDatetime(...) + timedelta` stays a
    # `FrozenDatetime`), and `ExpiresAt` requires `isinstance(value, datetime.datetime)`
    # which, once patched, means `isinstance(value, FrozenDatetime)`.
    state = Clock(FrozenDatetime(2024, 1, 1, 12, 0, 0))
    return state


@pytest.fixture
def make_expires_at(clock):
    def _make(*, minutes: int = 30) -> ExpiresAt:
        return ExpiresAt(clock.now + datetime.timedelta(minutes=minutes))

    return _make


@pytest.fixture
def make_portal(clock):
    def _make(
        *,
        portal_id: int = 1,
        name: str = "Test portal",
        world_destination: str = "Mars",
        stability: float = 9.0,  # safe but below PortalStability.max_value - at max, Risk.assess() now forces max risk
        energy: int = 0,
        expires_in_minutes: int = 30
    ) -> Portal:
        return Portal.create(
            portal_id=portal_id,
            name=name,
            world_destination=world_destination,
            stability=PortalStability(stability),
            energy=Energy(energy),
            expires_at=ExpiresAt(clock.now + datetime.timedelta(minutes=expires_in_minutes)),
        )

    return _make
