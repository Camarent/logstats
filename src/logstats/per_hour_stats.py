from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, time

from logstats.data import LogEntry, LogType


@dataclass(frozen=True)
class HourMessage:
    timestamp: datetime
    count: int


@dataclass(frozen=True)
class HourlyStats:
    source: str
    level: LogType | None
    total: int
    messages: list[HourMessage]


def compute_per_hour(
    entries: Iterable[LogEntry], source: str, *, level: LogType | None
) -> HourlyStats:
    messages = Counter((e.timestamp.date(), e.timestamp.hour) for e in entries)
    return HourlyStats(
        source,
        level,
        sum(messages.values()),
        [
            HourMessage(datetime.combine(day, time(hour=hour)), n)
            for (day, hour), n in sorted(messages.items())
        ],
    )
