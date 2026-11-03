from collections.abc import Callable, Sequence
from dataclasses import replace

import httpx

from logstats.data import LogEntry, LogType
from logstats.fetcher import collect
from logstats.source_parser import FetchedSource


def merge_entries(sources: Sequence[FetchedSource]) -> list[LogEntry]:
    return [line for fs in sources for line in fs.entries]


def build_stats[T](
    sources: Sequence[FetchedSource],
    combined: bool,
    compute: Callable[[Sequence[LogEntry], str], T],
) -> list[T]:
    if combined:
        return [compute(merge_entries(sources), "All")]
    else:
        return [compute(fs.entries, fs.source) for fs in sources]


async def gather_stats[T](
    sources: dict[str, str],
    level: LogType | None,
    combined: bool,
    client: httpx.AsyncClient,
    compute: Callable[[Sequence[LogEntry], str], T],
) -> tuple[list[T], list[FetchedSource]]:
    fetched = await collect(list(sources.values()), level, client)
    fetched = [
        replace(fs, source=name) for name, fs in zip(sources, fetched, strict=True)
    ]
    return build_stats(fetched, combined, compute), fetched
