from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from logstats.data import LogEntry, LogType
from logstats.source_parser import FetchedSource


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
    entries: Sequence[LogEntry], level: LogType | None, top: int, source: str
) -> TopStats:
    messages = Counter((e.level, e.message) for e in entries)
    return TopStats(
        source,
        top,
        level,
        len(entries),
        [MessageCount(lvl, msg, n) for (lvl, msg), n in messages.most_common(top)],
    )


def build_top(
    sources: Sequence[FetchedSource], level: LogType | None, top: int, combined: bool
) -> list[TopStats]:
    if combined:
        entries = [line for fs in sources for line in fs.log_lines]
        return [compute_top(entries, level, top, "All")]
    else:
        return [compute_top(fs.log_lines, level, top, fs.source) for fs in sources]
