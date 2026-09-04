import pytest

from domain.common import ValueObject
from domain.common.errors import DomainUnsupportedOperandTypeError, DomainWrongComparisonTypeError


class Point(ValueObject):
    pass


class OtherValueObject(ValueObject):
    pass


def test_value_property_returns_wrapped_value():
    assert Point(5).value == 5


def test_wrapping_another_instance_of_same_type_unwraps_it():
    assert Point(Point(5)).value == 5


def test_equal_when_same_type_and_same_value():
    assert Point(5) == Point(5)


def test_not_equal_when_same_type_different_value():
    assert Point(5) != Point(6)


def test_equal_to_raw_scalar_of_the_wrapped_type():
    assert Point(5) == 5
    assert 5 == Point(5)


def test_not_equal_to_different_value_object_type():
    assert Point(5) != OtherValueObject(5)


def test_not_equal_to_unrelated_type():
    assert Point(5) != "5"
    assert Point(5) != None  # noqa: E711


def test_equal_instances_have_equal_hash():
    assert hash(Point(5)) == hash(Point(5))


def test_can_be_used_as_dict_key_or_in_a_set():
    assert len({Point(1), Point(1), Point(2)}) == 2


class TestOrdering:
    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a <= b,
    ])
    def test_true_when_same_type_and_lesser_value(self, op):
        assert op(Point(1), Point(2))

    @pytest.mark.parametrize("op", [
        lambda a, b: a > b,
        lambda a, b: a >= b,
        lambda a, b: a >= b,
    ])
    def test_true_when_same_type_and_greater_value(self, op):
        assert op(Point(2), Point(1))

    def test_compares_against_a_raw_scalar_of_the_wrapped_type(self):
        assert Point(1) < 2
        assert Point(2) > 1
        assert Point(2) <= 2
        assert Point(2) >= 2

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_raises_when_compared_to_an_unrelated_type(self, op):
        with pytest.raises(DomainWrongComparisonTypeError):
            op(Point(1), "not a point")

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_raises_when_compared_to_a_different_value_object_type(self, op):
        with pytest.raises(DomainWrongComparisonTypeError):
            op(Point(1), OtherValueObject(1))


class TestArithmetic:
    def test_add_two_instances_of_the_same_type(self):
        result = Point(2) + Point(3)

        assert isinstance(result, Point)
        assert result.value == 5

    def test_add_a_raw_scalar_of_the_wrapped_type(self):
        result = Point(2) + 3

        assert isinstance(result, Point)
        assert result.value == 5

    def test_sub_two_instances_of_the_same_type(self):
        result = Point(5) - Point(2)

        assert isinstance(result, Point)
        assert result.value == 3

    def test_sub_a_raw_scalar_of_the_wrapped_type(self):
        result = Point(5) - 2

        assert isinstance(result, Point)
        assert result.value == 3

    def test_add_raises_for_an_unrelated_type(self):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            Point(1) + "not a point"

    def test_sub_raises_for_an_unrelated_type(self):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            Point(1) - "not a point"

    def test_add_raises_for_a_different_value_object_type(self):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            Point(1) + OtherValueObject(1)


class TestReflectedArithmetic:
    """`__radd__`/`__rsub__` cover `<raw scalar> + point` / `<raw scalar> -
    point` - only reached once the raw scalar's own `__add__`/`__sub__` has
    already given up (returned `NotImplemented`), which is exactly what
    happens for a plain `int` faced with a `Point`.
    """

    def test_radd_with_a_raw_scalar_of_the_wrapped_type(self):
        result = 3 + Point(2)

        assert isinstance(result, Point)
        assert result.value == 5

    def test_rsub_with_a_raw_scalar_of_the_wrapped_type(self):
        result = 5 - Point(2)

        assert isinstance(result, Point)
        assert result.value == 3

    def test_radd_raises_for_an_unrelated_type(self):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            "not a point" + Point(1)

    def test_rsub_raises_for_an_unrelated_type(self):
        with pytest.raises(DomainUnsupportedOperandTypeError):
            "not a point" - Point(1)
