from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, time

from logstats.data import LogEntry, LogType
from logstats.source_parser import FetchedSource


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
    entries: Sequence[LogEntry], level: LogType | None, source: str
) -> HourlyStats:
    messages = Counter((e.timestamp.date(), e.timestamp.hour) for e in entries)
    return HourlyStats(
        source,
        level,
        len(entries),
        [
            HourMessage(datetime.combine(day, time(hour=hour)), n)
            for (day, hour), n in sorted(messages.items())
        ],
    )


def build_per_hour(
    sources: Sequence[FetchedSource], level: LogType | None, combined: bool
) -> list[HourlyStats]:
    if combined:
        entries = [line for fs in sources for line in fs.log_lines]
        return [compute_per_hour(entries, level, "All")]
    else:
        return [compute_per_hour(fs.log_lines, level, fs.source) for fs in sources]
