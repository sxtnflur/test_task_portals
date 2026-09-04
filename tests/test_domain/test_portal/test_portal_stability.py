import pytest

from domain.common.errors import (
    DomainUnsupportedOperandTypeError,
    DomainValueError,
    DomainWrongComparisonTypeError,
    ValueObjectValueError,
)
from domain.portal.value_objects.stability import PortalStability


@pytest.mark.parametrize("value", [0, 0.0, 5.5, 10, 10.0])
def test_accepts_values_within_bounds_and_coerces_int_to_float(value):
    stability = PortalStability(value)

    assert stability.value == float(value)
    assert isinstance(stability.value, float)


@pytest.mark.parametrize("value", [-0.1, 10.1])
def test_rejects_values_out_of_bounds(value):
    with pytest.raises(DomainValueError):
        PortalStability(value)


def test_rejects_non_numeric_value():
    with pytest.raises(ValueObjectValueError):
        PortalStability("5.0")


@pytest.mark.parametrize(
    "value, is_full, is_middle, is_critical, level",
    [
        (10.0, True, False, False, "full"),
        (7.0, False, True, False, "middle"),
        (5.0, False, False, True, "critical"),
        (4.9, False, False, True, "critical"),
        (0.0, False, False, True, "critical"),
    ],
)
def test_classification_methods(value, is_full, is_middle, is_critical, level):
    stability = PortalStability(value)

    assert stability.is_full() is is_full
    assert stability.is_middle() is is_middle
    assert stability.is_critical() is is_critical
    assert stability.level() == level


def test_add_two_stability_objects():
    assert (PortalStability(3.0) + PortalStability(4.0)).value == 7.0


def test_add_a_raw_float():
    assert (PortalStability(3.0) + 4.0).value == 7.0


def test_sub_two_stability_objects():
    assert (PortalStability(7.0) - PortalStability(2.0)).value == 5.0


def test_sub_a_raw_float():
    assert (PortalStability(7.0) - 2.0).value == 5.0


def test_radd_float_to_stability():
    assert (4.0 + PortalStability(3.0)).value == 7.0


def test_rsub_stability_from_float():
    assert (7.0 - PortalStability(2.0)).value == 5.0


@pytest.mark.parametrize("other", [4, "4"])
def test_add_anything_other_than_a_stability_or_float_raises(other):
    # The value objects only accept an instance of their own type, or a raw
    # scalar of the *exact* type they wrap (`float` here) - `PortalStability`
    # itself coerces an int given to its constructor, but `__add__`/`__sub__`
    # do not: `int`/`Decimal` no longer work as operands, only `float` does.
    with pytest.raises(DomainUnsupportedOperandTypeError):
        PortalStability(3.0) + other


@pytest.mark.parametrize("other", [2, "2"])
def test_sub_anything_other_than_a_stability_or_float_raises(other):
    with pytest.raises(DomainUnsupportedOperandTypeError):
        PortalStability(7.0) - other


def test_add_out_of_bounds_raises():
    with pytest.raises(DomainValueError):
        PortalStability(9.5) + 1.0


def test_sub_out_of_bounds_raises():
    with pytest.raises(DomainValueError):
        PortalStability(1.0) - 2.0


class TestOrdering:
    def test_compares_two_stability_objects(self):
        assert PortalStability(3.0) < PortalStability(5.0)
        assert PortalStability(3.0) <= PortalStability(3.0)
        assert PortalStability(5.0) > PortalStability(3.0)
        assert PortalStability(3.0) >= PortalStability(3.0)

    def test_compares_against_a_raw_float(self):
        assert PortalStability(3.0) < 5.0
        assert PortalStability(5.0) > 3.0

    def test_does_not_compare_against_a_raw_int(self):
        # Same asymmetry as arithmetic: only an exact `float` (the wrapped
        # type) or another `PortalStability` is a valid operand.
        with pytest.raises(DomainWrongComparisonTypeError):
            PortalStability(3.0) < 5

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_raises_when_compared_to_an_unsupported_type(self, op):
        with pytest.raises(DomainWrongComparisonTypeError):
            op(PortalStability(3.0), "not a stability")
