import datetime

from domain.common.entity import Entity
from domain.common.errors import DomainValueError, UpdateToSameValueError

from domain.portal.enums import PortalStatusEnum, PortalActionEnum, PortalMethodEnum
from domain.portal.errors import InvalidPortalMethodError, ClosedPortalError, TooHighRiskError, TooLargeValueError
from domain.portal.value_objects.energy import Energy
from domain.portal.value_objects.expires_at import ExpiresAt
from domain.portal.value_objects.stability import PortalStability
from domain.risk.value_objects.risk import Risk, RiskFactorEnum


class Portal(Entity):
    def __init__(
            self,
            portal_id: int,
            name: str,
            world_destination: str,
            energy: Energy,
            stability: PortalStability,
            expires_at: ExpiresAt,
            count_observers: int,
            marked: bool,
            status: PortalStatusEnum
    ):
        self.__id = portal_id
        self.__name = name
        self.__world_destination = world_destination
        self.__stability = stability
        self.__energy = energy
        self.__expires_at = expires_at
        self.__count_observers = count_observers
        self.__marked = marked

        if expires_at.expired:
            status = PortalStatusEnum.closed

        self.__status = status

    @classmethod
    def create(
        cls,
        portal_id: int,
        name: str,
        world_destination: str,
        energy: Energy,
        stability: PortalStability,
        expires_at: ExpiresAt,
        count_observers: int = 0,
        status: PortalStatusEnum = PortalActionEnum.open,
        marked: bool = False
    ):
        return cls(
            portal_id=portal_id,
            name=name,
            world_destination=world_destination,
            energy=energy,
            stability=stability,
            expires_at=expires_at,
            count_observers=count_observers,
            marked=marked,
            status=status
        )

    def __hash__(self):
        return hash(self.__id)

    def __str__(self):
        return f"Portal #{self.id} {self.name!r} ({self.status.value})"

    def __repr__(self):
        return f"Portal {self.name!r}"

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def world_destination(self):
        return self.__world_destination

    @property
    def stability(self):
        """
        :return: PortalStability(float) between 0 and 10
        """
        return self.__stability

    @property
    def energy(self):
        """
        :return: Energy(int) between 0 and 10
        """
        return self.__energy

    @property
    def status(self):
        return self.__status

    @property
    def count_observers(self):
        """
        :return: Int - always more than or equals 0
        """
        return self.__count_observers

    @property
    def marked(self):
        return self.__marked

    @property
    def expires_at(self):
        return self.__expires_at

    @property
    def expires_in(self) -> datetime.timedelta:
        if self.is_closed:
            return datetime.timedelta(seconds=0)
        return self.__expires_at.expires_in

    @property
    def expired(self):
        return self.__expires_at.expired

    @property
    def is_open(self):
        return self.__status == PortalStatusEnum.open

    @property
    def is_closed(self):
        return self.__status == PortalStatusEnum.closed

    def get_risk(self) -> Risk | None:
        """
        :return: Risk(int) between 0 and 10, where 0 - min risk and 10 - max risk.
        If the portal is closed, returns None.
        """
        if self.is_closed:
            return

        return Risk.assess(
            stability=self.stability,
            energy=self.energy,
            expires_at=self.__expires_at
        )

    def change_status(self, status: PortalStatusEnum) -> None:
        if status == self.__status:
            raise UpdateToSameValueError(self, 'status', status.value)

        if status == PortalStatusEnum.closed:
            self.__expires_at = ExpiresAt.now()
            self.__stability = PortalStability(0.0)
            self.__energy = Energy(0)

        elif status == PortalStatusEnum.open:
            self.__expires_at = ExpiresAt.now() + datetime.timedelta(minutes=3)

        self.__status = status

    def close(self):
        if self.count_observers > 0:
            raise DomainValueError("You cannot close portal while there are observers in it")

        return self.change_status(PortalStatusEnum.closed)

    def open(self):
        return self.change_status(PortalStatusEnum.open)

    def stabilize(self) -> PortalStability:
        """
        :raise: DomainValueError - You cannot stabilize a closed portal
        :return: Float between 0 and 10, where 0 - min risk and 10 - max risk
        """
        self.raise_if_closed()
        self.__stability = PortalStability(min(self.__stability.value + 0.5, 10.0))
        return self.__stability

    def add_observer(self):
        self.raise_if_closed()

        if self.get_risk().high:
            raise TooHighRiskError

        self.__stability -= 0.5

        self.__count_observers += 1

    def take_observer(self):
        self.raise_if_closed()

        if self.__count_observers == 0:
            raise DomainValueError(f"No observers in the {self!r}")

        self.__count_observers -= 1

    def mark(self):
        """Mark as portal under a question"""
        self.raise_if_closed()
        if self.marked:
            raise UpdateToSameValueError(self, 'marked', True)
        self.__marked = True

    def unmark(self):
        """Cancel method mark()"""
        self.raise_if_closed()
        if not self.marked:
            raise UpdateToSameValueError(self, 'marked', False)
        self.__marked = False

    def raise_if_closed(self):
        if self.is_closed:
            raise ClosedPortalError

    def get_best_action(self) -> PortalActionEnum:
        """Return the highest-priority safe action for the current state.

        Priority: open for a closed portal, resolve emergency risk,
        restore critical stability, then send observers.
        """
        if self.is_closed:
            return PortalActionEnum.open

        risk = self.get_risk()
        main_risk_factor = risk.main_risk_factor

        if main_risk_factor is not None:
            if main_risk_factor.name == RiskFactorEnum.high_instability:
                return PortalActionEnum.stabilize

            if main_risk_factor.name == RiskFactorEnum.closing_soon:
                if self.count_observers > 0:
                    return PortalActionEnum.take_observers
                return PortalActionEnum.close

        return PortalActionEnum.add_observers

    def do_method(self, action: PortalMethodEnum):
        action_name: str = action.value
        method = getattr(self, action_name)
        if method is None:
            raise InvalidPortalMethodError(action_name)
        return method()
