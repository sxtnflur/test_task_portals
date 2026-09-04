from domain.common.errors import DomainValueError
from domain.portal.errors import ClosedPortalError, InvalidPortalMethodError


def test_invalid_portal_method_error_is_a_domain_value_error():
    error = InvalidPortalMethodError("teleport")

    assert isinstance(error, DomainValueError)
    assert "teleport" in str(error)


def test_closed_portal_error_is_a_domain_value_error():
    error = ClosedPortalError()

    assert isinstance(error, DomainValueError)
    assert str(error) == "Portal is closed"


def test_closed_portal_error_can_be_raised_bare():
    # `Portal.raise_if_closed()` does `raise ClosedPortalError` (no call
    # parens) - confirm the bare class raises fine with no required args.
    try:
        raise ClosedPortalError
    except ClosedPortalError as error:
        assert str(error) == "Portal is closed"
