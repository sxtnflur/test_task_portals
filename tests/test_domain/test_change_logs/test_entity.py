import datetime
import uuid
from unittest.mock import Mock

import pytest

from domain.change_logs import PortalChangeLog
from domain.change_logs import PortalChangeLogAction
from domain.common.errors import DomainWrongComparisonTypeError


ACTED_AT = datetime.datetime(2024, 1, 1, 10, 30, 0)


def make_log(**overrides):
    params = dict(
        portal_id=1,
        action=PortalChangeLogAction.opened,
        detail=None,
        acted_at=ACTED_AT,
    )
    params.update(overrides)
    return PortalChangeLog.create(**params)


def test_create_generates_a_uuid_id():
    log = make_log()

    assert isinstance(log.id, uuid.UUID)


def test_create_uses_the_given_acted_at():
    log = make_log(acted_at=ACTED_AT)

    assert log.acted_at == ACTED_AT


def test_create_defaults_acted_at_to_now(clock):
    log = PortalChangeLog.create(portal_id=1, action=PortalChangeLogAction.opened)

    assert log.acted_at == clock.now


def test_exposes_the_given_attributes():
    log = make_log(portal_id=5, action=PortalChangeLogAction.marked, detail="note")

    assert log.portal_id == 5
    assert log.action == PortalChangeLogAction.marked
    assert log.detail == "note"


def test_str_without_detail():
    log = make_log(portal_id=3, action=PortalChangeLogAction.closed, detail=None, acted_at=ACTED_AT)

    assert str(log) == "Portal #3 got action 'closed' at 01.01.2024 10:30"


def test_str_with_detail():
    log = make_log(portal_id=3, action=PortalChangeLogAction.closed, detail="manual", acted_at=ACTED_AT)

    assert str(log) == "Portal #3 got action 'closed' at 01.01.2024 10:30: (manual)"


def test_repr_includes_id_and_str():
    log = make_log()

    assert repr(log) == f"PortalChangeLog #{log.id} ({log})"


def test_log_text_matches_str():
    log = make_log()

    assert log.log_text == str(log)


def test_to_dict_contains_all_fields():
    log = make_log(portal_id=2, action=PortalChangeLogAction.marked, detail="x", acted_at=ACTED_AT)

    assert log.to_dict() == {
        "id": log.id,
        "action": "marked",
        "portal_id": 2,
        "acted_at": ACTED_AT,
        "detail": "x",
    }


def test_log_writes_to_the_given_logger():
    log = make_log()
    logger = Mock()

    log.log(logger)

    logger.info.assert_called_once_with(log.log_text)


def test_log_falls_back_to_a_default_logger(caplog):
    log = make_log()

    with caplog.at_level("INFO", logger="Portal Chage Log"):
        log.log()

    assert log.log_text in caplog.text


class TestEqualityAndOrdering:
    def test_equal_when_acted_at_matches(self):
        a = make_log(acted_at=ACTED_AT)
        b = make_log(acted_at=ACTED_AT)

        assert a == b

    def test_not_equal_when_acted_at_differs(self):
        a = make_log(acted_at=ACTED_AT)
        b = make_log(acted_at=ACTED_AT + datetime.timedelta(seconds=1))

        assert not (a == b)

    def test_ordering_reflects_acted_at(self):
        earlier = make_log(acted_at=ACTED_AT)
        later = make_log(acted_at=ACTED_AT + datetime.timedelta(minutes=1))

        assert earlier < later
        assert earlier <= later
        assert later > earlier
        assert later >= earlier

    def test_hash_depends_only_on_id(self):
        log = make_log()

        assert hash(log) == hash(log.id)

    @pytest.mark.parametrize("op", [
        lambda a, b: a < b,
        lambda a, b: a <= b,
        lambda a, b: a > b,
        lambda a, b: a >= b,
    ])
    def test_ordering_against_an_unrelated_type_raises(self, op):
        # `PortalChangeLog` no longer defines its own comparison dunders; it
        # inherits `Entity`'s generic ones (with `comparison_field = 'acted_at'`).
        with pytest.raises(DomainWrongComparisonTypeError):
            op(make_log(), "not a change log")
