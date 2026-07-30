from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from logstats.data import LogEntry, LogType


@dataclass(frozen=True)
class MessageCount:
    level: LogType
    message: str
    count: int


@dataclass(frozen=True)
class TopStats:
    source: str
    top: int
    level: LogType | None
    total: int
    messages: list[MessageCount]


def compute_top(
    entries: Sequence[LogEntry], source: str, *, level: LogType | None, top: int
) -> TopStats:
    messages = Counter((e.level, e.message) for e in entries)
    return TopStats(
        source,
        top,
        level,
        len(entries),
        [MessageCount(lvl, msg, n) for (lvl, msg), n in messages.most_common(top)],
    )
