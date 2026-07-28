from collections.abc import Sequence
from dataclasses import replace
from functools import partial

import httpx
from pydantic import BaseModel

from logstats.data import LogType, get_name_capitalize
from logstats.parser import collect
from logstats.source_parser import FetchedSource
from logstats.stats import build_stats
from logstats.top_stats import TopStats, compute_top


class MessageCountOut(BaseModel):
    level: str
    message: str
    count: int


class TopStatsOut(BaseModel):
    source: str
    level: str
    top: int
    total: int
    messages: list[MessageCountOut]


class SourceError(BaseModel):
    source: str
    error: str


class TopResponse(BaseModel):
    results: list[TopStatsOut]
    errors: list[SourceError] = []


def to_response(stats: list[TopStats], fetched: Sequence[FetchedSource]) -> TopResponse:
    return TopResponse(
        results=[
            TopStatsOut(
                source=s.source,
                level=get_name_capitalize(s.level),
                top=s.top,
                total=s.total,
                messages=[
                    MessageCountOut(
                        level=m.level.name.capitalize(),
                        message=m.message,
                        count=m.count,
                    )
                    for m in s.messages
                ],
            )
            for s in stats
        ],
        errors=[
            SourceError(source=fs.source, error=fs.error)
            for fs in fetched
            if fs.error is not None
        ],
    )


async def gather_top_stats(
    sources: dict[str, str],
    level: LogType | None,
    top: int,
    combined: bool,
    client: httpx.AsyncClient,
) -> TopResponse:
    fetched = await collect(list(sources.values()), level, client)
    fetched = [replace(fs, source=name) for name, fs in zip(sources, fetched)]
    stats = build_stats(fetched, combined, partial(compute_top, level=level, top=top))
    return to_response(stats, fetched)
