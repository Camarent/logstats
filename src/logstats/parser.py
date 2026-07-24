import asyncio
import logging
from collections.abc import Sequence

import httpx

from logstats.data import LogType
from logstats.source_parser import FetchedSource, fetch_source

logger = logging.getLogger(__name__)


async def fetch(sources: Sequence[str], level: LogType | None) -> list[FetchedSource]:
    async with httpx.AsyncClient() as client:
        return await collect(sources, level, client)


async def collect(
    sources: Sequence[str], level: LogType | None, client: httpx.AsyncClient
) -> list[FetchedSource]:
    results: list[asyncio.Task[FetchedSource]] = []
    async with asyncio.TaskGroup() as group:
        for s in sources:
            task = fetch_source(s, level, client)
            if task is not None:
                results.append(group.create_task(task))
    return [t.result() for t in results]
