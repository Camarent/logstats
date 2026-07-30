import logging
from collections.abc import AsyncIterator, Sequence
from datetime import datetime
from functools import partial
from typing import Literal

import httpx
from pydantic import BaseModel

from logstats.data import LogType, get_name_capitalize
from logstats.per_hour_stats import HourlyStats, compute_per_hour
from logstats.source_parser import FetchedSource, stream_entries
from logstats.stats import gather_stats
from logstats.top_stats import TopStats, compute_top

logger = logging.getLogger(__name__)


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


class SseEvent(BaseModel):
    type: str

    def to_sse(self) -> str:
        return f"event: {self.type}\ndata: {self.model_dump_json()}\n\n"


class EntryEvent(SseEvent):
    type: Literal["entry"] = "entry"
    source: str
    level: str
    timestamp: datetime
    message: str


class SourceErrorEvent(SseEvent):
    type: Literal["source_error"] = "source_error"
    source: str
    error: str


async def stream_all(
    sources: dict[str, str], level: LogType | None, client: httpx.AsyncClient
) -> AsyncIterator[str]:
    for name, url in sources.items():
        try:
            async for entry in stream_entries(url, level, client):
                entry_out = EntryEvent(
                    source=name,
                    timestamp=entry.timestamp,
                    level=entry.level.name.capitalize(),
                    message=entry.message,
                )
                yield entry_out.to_sse()
        except (httpx.HTTPError, OSError) as exc:
            logger.warning(f"failed to stream {name}: {exc}")
            err = SourceErrorEvent(source=name, error=str(exc))
            yield err.to_sse()
