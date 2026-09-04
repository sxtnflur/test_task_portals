from domain.common.errors import DomainError

from application import NotFoundError, PortalNotFoundError, ServiceError


def test_service_error_is_a_domain_error():
    assert isinstance(ServiceError("boom"), DomainError)


def test_not_found_error_is_a_service_error_and_a_lookup_error():
    error = NotFoundError("missing")

    assert isinstance(error, ServiceError)
    assert isinstance(error, LookupError)


def test_portal_not_found_error_is_a_not_found_error():
    error = PortalNotFoundError("Portal with id 1 was not found")

    assert isinstance(error, NotFoundError)
    assert str(error) == "Portal with id 1 was not found"


def test_portal_not_found_error_can_be_caught_as_lookup_error():
    try:
        raise PortalNotFoundError("missing")
    except LookupError as error:
        assert isinstance(error, PortalNotFoundError)
    else:
        assert False, "expected LookupError to be raised"
