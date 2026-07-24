import asyncio

import httpx

from logstats.parser import collect
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
    assert (sum(len(r.log_lines) for r in result)) == 4


def test_unknown_source_types():
    logs = {
        "ftp://logs.test/app1.log": "2026-07-13T09:15:42 INFO Starting\n2026-07-13T09:22:10 ERROR Boom"
    }
    result = asyncio.run(collect_logs(logs))
    assert {r.source for r in result} == set(logs)
    assert (sum(len(r.log_lines) for r in result)) == 0


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
    assert len(by_source["http://x/good.log"].log_lines) == 1  # good one still parsed
    assert by_source["http://x/bad.log"].error is not None  # bad one flagged, not fatal
