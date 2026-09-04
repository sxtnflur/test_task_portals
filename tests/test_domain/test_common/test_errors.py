import pytest

from domain.common.errors import (
    DomainError,
    DomainTypeError,
    DomainUnsupportedOperandTypeError,
    DomainValueError,
    DomainWrongComparisonTypeError,
    ValueObjectValueError,
)
from domain.common import ValueObject


class Dummy(ValueObject):
    pass


def test_domain_error_str_is_the_message():
    error = DomainError("something went wrong")

    assert str(error) == "something went wrong"
    assert error.message == "something went wrong"


def test_domain_error_repr_includes_class_name_and_message():
    assert repr(DomainError("boom")) == "DomainError(boom)"


def test_domain_value_error_is_also_a_value_error():
    assert isinstance(DomainValueError("bad value"), ValueError)
    assert isinstance(DomainValueError("bad value"), DomainError)


def test_domain_value_error_can_be_raised_and_caught_as_value_error():
    with pytest.raises(ValueError):
        raise DomainValueError("bad value")


def test_domain_type_error_is_a_domain_error():
    assert isinstance(DomainTypeError("bad type"), DomainError)


def test_value_object_value_error_reports_the_expected_type():
    error = ValueObjectValueError(Dummy(1), int)

    assert "Dummy" in error.message
    assert "int" in error.message


def test_domain_unsupported_operand_type_error_message():
    error = DomainUnsupportedOperandTypeError(int, str, "+")

    assert isinstance(error, DomainError)
    assert str(error) == "unsupported operand type(s) for +: 'int' and 'str'"


def test_domain_wrong_comparison_type_error_message():
    error = DomainWrongComparisonTypeError(int, str, ">")

    assert isinstance(error, DomainError)
    assert str(error) == f"'>' not supported between instances of '{int}' and '{str}'"
