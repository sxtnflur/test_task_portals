from domain.change_logs.entity import PortalChangeLog

from infra.repositories.memory.base import PortalChangeLogsRepository


class MemoryPortalChangeLogsRepository(PortalChangeLogsRepository):
    def __init__(self):
        self.__logs = set()

    async def add(self, log: PortalChangeLog) -> None:
        self.__logs.add(log)

    async def get_list(self, offset: int = 0, limit: int = 10, desc: bool = True) -> list[PortalChangeLog]:
        logs = list(self.__logs)

        if desc:
            logs.reverse()

        if offset == 0 and limit > len(logs):
            return logs

        if offset > 0 and limit > len(logs):
            return logs[offset:]

        if offset == 0 and limit <= len(logs):
            return logs[:logs]

        return logs[offset:limit]
