import logging

import pytest

from logstats.core import create_reports, main
from logstats.data import ReportRequest
from logstats.source_parser import FetchedSource


def test_no_source_fetched(monkeypatch, caplog):
    async def fake_fetch(sources, level):
        return []

    monkeypatch.setattr("logstats.core.fetch", fake_fetch)
    with caplog.at_level(logging.WARNING):
        main(["test.log"], None, None, False, False)
    assert "No available sources" in caplog.text


@pytest.mark.parametrize(
    "req, expected_header",
    [
        (ReportRequest(None, 1, False, False), "[app1.log] Top 1 All messages:"),
        (ReportRequest(None, None, True, False), "[app1.log] All messages per hour:"),
        (ReportRequest(None, None, False, False), ""),
    ],
)
def test_run_output_correct_report(req: ReportRequest, expected_header: str):
    reports = create_reports([FetchedSource([], "app1.log")], req)
    assert all(r.build_header() == expected_header for r in reports)
