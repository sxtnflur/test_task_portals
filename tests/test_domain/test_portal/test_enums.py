from domain.portal.enums import PortalActionEnum, PortalMethodEnum, PortalStatusEnum


def test_portal_status_values():
    assert PortalStatusEnum.open == "open"
    assert PortalStatusEnum.closed == "closed"


def test_portal_action_values():
    assert {action.value for action in PortalActionEnum} == {
        "open",
        "close",
        "mark",
        "stabilize",
        "add_observers",
        "take_observers",
    }


def test_portal_method_values_match_real_portal_methods():
    # `Portal.do_method()` dispatches by calling `getattr(portal, action.value)`,
    # so every member here must name an actual zero-argument `Portal` method.
    assert {method.value for method in PortalMethodEnum} == {
        "open",
        "close",
        "mark",
        "unmark",
        "add_observer",
        "take_observer",
        "stabilize",
    }
