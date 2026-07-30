from collections.abc import Sequence
from datetime import datetime
from functools import partial

import httpx
from pydantic import BaseModel

from logstats.data import LogType, get_name_capitalize
from logstats.per_hour_stats import HourlyStats, compute_per_hour
from logstats.source_parser import FetchedSource
from logstats.stats import gather_stats
from logstats.top_stats import TopStats, compute_top


class SourceError(BaseModel):
    source: str
    error: str


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


class TopResponse(BaseModel):
    results: list[TopStatsOut]
    errors: list[SourceError] = []


def to_top_response(
    stats: list[TopStats], fetched: Sequence[FetchedSource]
) -> TopResponse:
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
    (stats, fetched) = await gather_stats(
        sources,
        level,
        combined,
        client,
        partial(compute_top, level=level, top=top),
    )
    return to_top_response(stats, fetched)


class HouryMessageOut(BaseModel):
    timestamp: datetime
    count: int


class HourlyStatsOut(BaseModel):
    source: str
    level: str
    total: int
    messages: list[HouryMessageOut]


class PerHourResponse(BaseModel):
    results: list[HourlyStatsOut]
    errors: list[SourceError] = []


def top_per_hour_response(
    stats: list[HourlyStats], fetched: Sequence[FetchedSource]
) -> PerHourResponse:
    return PerHourResponse(
        results=[
            HourlyStatsOut(
                source=s.source,
                level=get_name_capitalize(s.level),
                total=s.total,
                messages=[
                    HouryMessageOut(timestamp=m.timestamp, count=m.count)
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


async def gather_per_hour_stats(
    sources: dict[str, str],
    level: LogType | None,
    combined: bool,
    client: httpx.AsyncClient,
) -> PerHourResponse:
    (stats, fetched) = await gather_stats(
        sources, level, combined, client, partial(compute_per_hour, level=level)
    )
    return top_per_hour_response(stats, fetched)
