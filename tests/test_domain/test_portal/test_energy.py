import pytest

from domain.common.errors import (
    DomainUnsupportedOperandTypeError,
    DomainValueError,
    DomainWrongComparisonTypeError,
    ValueObjectValueError,
)
from domain.portal.value_objects.energy import Energy


@pytest.mark.parametrize("value", [0, 5, 10])
def test_accepts_values_within_bounds(value):
    assert Energy(value).value == value


@pytest.mark.parametrize("value", [-1, 11])
def test_rejects_values_out_of_bounds(value):
    with pytest.raises(DomainValueError):
        Energy(value)


def test_rejects_non_int_value():
    with pytest.raises(ValueObjectValueError):
        Energy(5.0)


@pytest.mark.parametrize("value, expected", [(6, False), (7, True), (10, True)])
def test_is_high_threshold(value, expected):
    assert Energy(value).is_high() is expected


def test_add_two_energy_objects():
    assert (Energy(3) + Energy(4)).value == 7


def test_add_int_to_energy():
    assert (Energy(3) + 4).value == 7


def test_sub_two_energy_objects():
    assert (Energy(7) - Energy(2)).value == 5


def test_sub_int_from_energy():
    assert (Energy(7) - 2).value == 5


def test_add_out_of_bounds_raises():
    with pytest.raises(DomainValueError):
        Energy(9) + 5


def test_sub_out_of_bounds_raises():
    with pytest.raises(DomainValueError):
        Energy(2) - 5


def test_radd_int_to_energy():
    assert (4 + Energy(3)).value == 7


def test_rsub_energy_from_int():
    assert (7 - Energy(2)).value == 5


def test_add_unsupported_type_raises_unsupported_operand_type_error():
    with pytest.raises(DomainUnsupportedOperandTypeError):
        Energy(3) + "4"


def test_sub_unsupported_type_raises_unsupported_operand_type_error():
    with pytest.raises(DomainUnsupportedOperandTypeError):
        Energy(3) - "4"


class TestOrdering:
    def test_compares_two_energy_objects(self):
        assert Energy(3) < Energy(5)
        assert Energy(3) <= Energy(3)
        assert Energy(5) > Energy(3)
        assert Energy(3) >= Energy(3)

    def test_compares_against_a_raw_int(self):
        assert Energy(3) < 5
        assert Energy(5) > 3
        assert Energy(3) <= 3
        assert Energy(3) >= 3

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_raises_when_compared_to_an_unsupported_type(self, op):
        with pytest.raises(DomainWrongComparisonTypeError):
            op(Energy(3), "not an energy")
