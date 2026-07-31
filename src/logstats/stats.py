from collections.abc import Callable, Sequence
from dataclasses import replace
from typing import TypeVar

import httpx

from logstats.data import LogEntry, LogType
from logstats.fetcher import collect
from logstats.source_parser import FetchedSource

T = TypeVar("T")


def merge_entries(sources: Sequence[FetchedSource]) -> list[LogEntry]:
    return [line for fs in sources for line in fs.entries]


def build_stats(
    sources: Sequence[FetchedSource],
    combined: bool,
    compute: Callable[[Sequence[LogEntry], str], T],
) -> list[T]:
    if combined:
        return [compute(merge_entries(sources), "All")]
    else:
        return [compute(fs.entries, fs.source) for fs in sources]


async def gather_stats(
    sources: dict[str, str],
    level: LogType | None,
    combined: bool,
    client: httpx.AsyncClient,
    compute: Callable[[Sequence[LogEntry], str], T],
) -> tuple[list[T], list[FetchedSource]]:
    fetched = await collect(list(sources.values()), level, client)
    fetched = [replace(fs, source=name) for name, fs in zip(sources, fetched)]
    return build_stats(fetched, combined, compute), fetched
