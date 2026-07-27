import asyncio
import time

import httpx

from logstats.parser import collect
from logstats.source_parser import FetchedSource


def test_concurrent_fetch_overlaps():
    delay = 0.1
    urls = [f"http://logs.test/app{i}.log" for i in range(5)]

    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(delay)
        return httpx.Response(200, text="2026-07-13T09:00:00 INFO ok")

    async def run() -> list[FetchedSource]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await collect(urls, None, client)

    start = time.perf_counter()
    result = asyncio.run(run())
    elapsed = time.perf_counter() - start

    print(f"\nconcurent elapsed time: {elapsed:.3f}s")

    assert len(result) == 5

    assert elapsed < delay * 2
