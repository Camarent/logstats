import asyncio

import httpx

from logstats.fetcher import collect
from logstats.source_parser import FetchedSource


async def collect_logs(responses: dict[str, str]) -> list[FetchedSource]:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=responses[str(request.url)])

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        return await collect(list(responses), None, client)


def test_parse_fetches():
    logs = {
        "http://logs.test/app1.log": "2026-07-13T09:15:42 INFO Starting\n2026-07-13T09:22:10 ERROR Boom",
        "http://logs.test/app2.log": "2026-07-13T10:11:08 WARNING Disk\n2026-07-13T10:52:03 ERROR Crash",
    }
    result = asyncio.run(collect_logs(logs))
    assert {r.source for r in result} == set(logs)
    assert (sum(len(r.entries) for r in result)) == 4


def test_unknown_source_types():
    logs = {
        "ftp://logs.test/app1.log": "2026-07-13T09:15:42 INFO Starting\n2026-07-13T09:22:10 ERROR Boom"
    }
    result = asyncio.run(collect_logs(logs))
    assert {r.source for r in result} == set(logs)
    assert (sum(len(r.entries) for r in result)) == 0


def test_collect_never_exceeds_max_concurrent():
    in_flight = 0
    peak = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        await asyncio.sleep(0.01)
        in_flight -= 1
        return httpx.Response(200, text="2026-07-13T09:00:00 INFO ok")

    async def run() -> list[FetchedSource]:
        sources = [f"http://x/app{i}.log" for i in range(8)]
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await collect(sources, None, client, max_concurrent=3)

    result = asyncio.run(run())
    assert len(result) == 8
    assert peak == 3


def test_connectivity_issues():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/good.log":
            return httpx.Response(200, text="2026-07-13T09:00:00 ERROR ok")
        return httpx.Response(500)

    async def run() -> list[FetchedSource]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await collect(
                ["http://x/good.log", "http://x/bad.log"], None, client
            )

    by_source = {r.source: r for r in asyncio.run(run())}
    assert len(by_source["http://x/good.log"].entries) == 1  # good one still parsed
    assert by_source["http://x/bad.log"].error is not None  # bad one flagged, not fatal
