import asyncio
import logging
from collections.abc import Sequence

import httpx

from logstats.data import LogType
from logstats.source_parser import FetchedSource, fetch_source

logger = logging.getLogger(__name__)

MAX_CONCURRENT_FETCHES = 10
TIMEOUT = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)


async def fetch(sources: Sequence[str], level: LogType | None) -> list[FetchedSource]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        return await collect(sources, level, client)


async def collect(
    sources: Sequence[str],
    level: LogType | None,
    client: httpx.AsyncClient,
    max_concurrent: int = MAX_CONCURRENT_FETCHES,
) -> list[FetchedSource]:
    limit = asyncio.Semaphore(max_concurrent)

    async def fetch_one(source: str) -> FetchedSource:
        async with limit:
            return await fetch_source(source, level, client)

    async with asyncio.TaskGroup() as group:
        results = [group.create_task(fetch_one(s)) for s in sources]
    return [t.result() for t in results]
