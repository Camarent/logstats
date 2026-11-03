from typing import Annotated

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import Field, TypeAdapter

from logstats.api import app, get_client, get_settings
from logstats.config import Settings
from logstats.schemas import EntryEvent, PerHourResponse, SourceErrorEvent, TopResponse

APP1_LOGS = (
    "2026-07-13T09:15:42 ERROR Boom\n"
    "2026-07-13T09:22:10 ERROR Boom\n"
    "2026-07-13T10:01:00 INFO Fine"
)

APP2_LOGS = "2026-07-13T09:15:43 ERROR Boom\n2026-07-13T10:01:00 INFO Fine"

SOURCES = {
    "app1": "http://logs.test/app1.log",
    "app2": "http://logs.test/app2.log",
    "bad": "http://logs.test/bad.log",
}


def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/app1.log":
        return httpx.Response(200, text=APP1_LOGS)
    if request.url.path == "/app2.log":
        return httpx.Response(200, text=APP2_LOGS)
    return httpx.Response(500)


@pytest.fixture
def api():
    mock = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    app.dependency_overrides[get_settings] = lambda: Settings(sources=SOURCES)
    app.dependency_overrides[get_client] = lambda: mock
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_reports_ok(api):
    response = api.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_app_boots_and_serves(tmp_path, monkeypatch):
    log = tmp_path / "app.log"
    log.write_text(APP1_LOGS)

    cfg = tmp_path / "sources.toml"
    cfg.write_text(f'[sources]\napp1 = "{log}"\n')
    monkeypatch.setenv("LOGSTATS_SOURCES", str(cfg))

    with TestClient(app) as client:
        r = client.get("/stats/top", params={"sources": "app1"})

    assert r.status_code == 200
    body = TopResponse.model_validate(r.json())
    assert body.results[0].messages[0].count == 2


def test_top_format_is_stable(api):
    body = api.get("/stats/top", params={"sources": "app1", "top": 1}).json()
    assert set(body) == {"results", "errors"}
    assert set(body["results"][0]) == {"source", "level", "top", "total", "messages"}
    assert set(body["results"][0]["messages"][0]) == {"level", "message", "count"}


def test_top_returns_counts(api):
    response = api.get("/stats/top", params={"sources": "app1", "top": 1}).json()
    body = TopResponse.model_validate(response)
    assert body.results[0].messages[0].count == 2
    assert body.results[0].messages[0].message == "Boom"


def test_top_filter_level_returns_counts(api):
    response = api.get(
        "/stats/top", params={"sources": "app1", "level": "INFO", "top": 1}
    ).json()
    body = TopResponse.model_validate(response)
    assert body.results[0].messages[0].count == 1
    assert body.results[0].messages[0].message == "Fine"


def test_failed_source_is_reported_not_fatal(api):
    response = api.get(
        "/stats/top", params={"sources": ["app1", "bad"], "top": 1}
    ).json()
    body = TopResponse.model_validate(response)
    assert body.errors[0].source == "bad"
    assert body.results[0].total == 3


def test_top_combines_sources(api):
    params = {"sources": ["app1", "app2"], "combined": "true"}
    response = api.get("/stats/top", params=params).json()
    body = TopResponse.model_validate(response)
    assert len(body.results) == 1
    assert body.results[0].source == "All"
    assert body.results[0].messages[0].count == 3


@pytest.mark.parametrize(
    "params",
    [
        {"sources": "nope"},
        {"sources": "app1", "level": "NOPE"},
        {"sources": "app1", "top": 0},
    ],
    ids=["unknown-source", "unknown-level", "top-below-one"],
)
def test_invalid_requests_are_rejected(api, params):
    assert api.get("/stats/top", params=params).status_code == 422


def test_per_hour_format_is_stable(api):
    body = api.get("/stats/per-hour", params={"sources": "app1"}).json()
    assert set(body) == {"results", "errors"}
    assert set(body["results"][0]) == {"source", "level", "total", "messages"}
    assert set(body["results"][0]["messages"][0]) == {"count", "timestamp"}


def test_per_hour_returns_counts(api):
    response = api.get("/stats/per-hour", params={"sources": "app1"}).json()
    body = PerHourResponse.model_validate(response)
    assert body.results[0].messages[0].count == 2
    assert body.results[0].messages[0].timestamp.hour == 9


def test_per_hour_filter_level_returns_counts(api):
    response = api.get(
        "/stats/per-hour", params={"sources": "app1", "level": "INFO"}
    ).json()
    body = PerHourResponse.model_validate(response)
    assert body.results[0].messages[0].count == 1
    assert body.results[0].messages[0].timestamp.hour == 10


def test_per_hour_failed_source_is_reported_not_fatal(api):
    response = api.get("/stats/per-hour", params={"sources": ["app1", "bad"]}).json()
    body = PerHourResponse.model_validate(response)
    assert body.errors[0].source == "bad"
    assert body.results[0].total == 3


def test_per_hour_combines_sources(api):
    params = {"sources": ["app1", "app2"], "combined": "true"}
    response = api.get("/stats/per-hour", params=params).json()
    body = PerHourResponse.model_validate(response)
    assert len(body.results) == 1
    assert body.results[0].source == "All"
    assert body.results[0].messages[0].count == 3


StreamEvent = Annotated[EntryEvent | SourceErrorEvent, Field(discriminator="type")]
stream_event_adapter: TypeAdapter[StreamEvent] = TypeAdapter(StreamEvent)


def read_events(response: httpx.Response) -> list[StreamEvent]:
    return [
        stream_event_adapter.validate_json(line.removeprefix("data: "))
        for line in response.iter_lines()
        if line.startswith("data: ")
    ]


def test_regular_reports(api):
    with api.stream("GET", "/stats/regular", params={"sources": ["app1"]}) as r:
        events = read_events(r)
    assert isinstance(events[0], EntryEvent)
    assert events[0].level == "Error"
    assert events[0].message == "Boom"


def test_regular_reports_failed_source_inline(api):
    with api.stream("GET", "/stats/regular", params={"sources": ["bad", "app1"]}) as r:
        events = read_events(r)

    assert isinstance(events[0], SourceErrorEvent)
    assert events[0].source == "bad"
    assert sum(isinstance(e, EntryEvent) for e in events) == 3
