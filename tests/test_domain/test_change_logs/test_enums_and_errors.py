from domain.change_logs import PortalChangeLogAction


def test_action_values_are_plain_strings():
    assert PortalChangeLogAction.opened.value == "opened"
    assert PortalChangeLogAction.opened == "opened"
