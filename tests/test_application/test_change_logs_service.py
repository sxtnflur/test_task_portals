from domain.change_logs import PortalChangeLogAction


async def test_create_log_persists_and_returns_the_log(change_logs_service, change_logs_repository):
    log = await change_logs_service.create_log(
        portal_id=7, action=PortalChangeLogAction.opened, detail="manual"
    )

    assert log.portal_id == 7
    assert log.action == PortalChangeLogAction.opened
    assert log.detail == "manual"
    assert change_logs_repository.logs == [log]


async def test_create_log_defaults_detail_and_acted_at(change_logs_service, clock):
    log = await change_logs_service.create_log(portal_id=1, action=PortalChangeLogAction.closed)

    assert log.detail is None
    assert log.acted_at == clock.now


async def test_get_list_returns_logs_ordered_by_most_recent_first(change_logs_service, clock):
    first = await change_logs_service.create_log(portal_id=1, action=PortalChangeLogAction.opened)
    clock.advance(minutes=1)
    second = await change_logs_service.create_log(portal_id=1, action=PortalChangeLogAction.closed)

    result = await change_logs_service.get_list()

    assert [log.action for log in result] == [second.action, first.action]


async def test_get_list_respects_offset_and_limit(change_logs_service):
    for _ in range(3):
        await change_logs_service.create_log(portal_id=1, action=PortalChangeLogAction.marked)

    result = await change_logs_service.get_list(offset=1, limit=1)

    assert len(result) == 1
