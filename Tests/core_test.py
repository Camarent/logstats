import logging

import pytest

from logstats.core import create_reports, main
from logstats.data import ReportRequest
from logstats.report import (
    PerHourReportFormatted,
    RegularReportFormatted,
    TopReportFormatted,
)
from logstats.source_parser import FetchedSource


def test_no_source_fetched(monkeypatch, caplog):
    async def fake_fetch(sources, level):
        return []

    monkeypatch.setattr("logstats.core.fetch", fake_fetch)
    with caplog.at_level(logging.WARNING):
        main(["test.log"], None, None, False, False)
    assert "No available sources" in caplog.text


@pytest.mark.parametrize(
    "req, report_type",
    [
        (ReportRequest(None, 1, False, False), TopReportFormatted),
        (ReportRequest(None, None, True, False), PerHourReportFormatted),
        (ReportRequest(None, None, False, False), RegularReportFormatted),
    ],
)
def test_run_output_correct_report(req: ReportRequest, report_type: type):
    reports = create_reports([FetchedSource([], "")], req)
    assert all(type(r) is report_type for r in reports)
