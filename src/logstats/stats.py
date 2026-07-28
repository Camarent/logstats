from collections.abc import Callable, Sequence
from typing import TypeVar

from logstats.data import LogEntry
from logstats.source_parser import FetchedSource

T = TypeVar("T")


def merge_entries(sources: Sequence[FetchedSource]) -> list[LogEntry]:
    return [line for fs in sources for line in fs.log_lines]


def build_stats(
    sources: Sequence[FetchedSource],
    combined: bool,
    compute: Callable[[Sequence[LogEntry], str], T],
) -> list[T]:
    if combined:
        return [compute(merge_entries(sources), "All")]
    else:
        return [compute(fs.log_lines, fs.source) for fs in sources]
