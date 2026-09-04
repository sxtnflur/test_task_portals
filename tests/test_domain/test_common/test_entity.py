import pytest

from domain.common import Entity
from domain.common.errors import DomainWrongComparisonTypeError


class Widget(Entity):
    pass


class Gadget(Entity):
    pass


def test_equal_when_same_type_and_same_id():
    assert Widget(id=1) == Widget(id=1)


def test_not_equal_when_same_type_different_id():
    assert Widget(id=1) != Widget(id=2)


def test_not_equal_when_different_type_same_id():
    assert Widget(id=1) != Gadget(id=1)


def test_hash_depends_only_on_id():
    assert hash(Widget(id=1)) == hash(Widget(id=1))


def test_str_and_repr_include_class_name_and_id():
    widget = Widget(id=42)

    assert str(widget) == "Widget(42)"
    assert repr(widget) == "Widget(42)"


class TestOrdering:
    def test_lt_and_le_compare_by_id(self):
        assert Widget(id=1) < Widget(id=2)
        assert Widget(id=1) <= Widget(id=1)
        assert not (Widget(id=2) < Widget(id=1))

    def test_gt_and_ge_compare_by_id(self):
        assert Widget(id=2) > Widget(id=1)
        assert Widget(id=1) >= Widget(id=1)
        assert not (Widget(id=1) > Widget(id=2))

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_raises_when_compared_to_an_unrelated_type(self, op):
        with pytest.raises(DomainWrongComparisonTypeError):
            op(Widget(id=1), "not an entity")

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_raises_when_compared_to_a_different_entity_type(self, op):
        with pytest.raises(DomainWrongComparisonTypeError):
            op(Widget(id=1), Gadget(id=1))
