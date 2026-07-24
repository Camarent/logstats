import pytest

from logstats.data import LogEntry, ReportRequest
from logstats.report import (
    PerHourReport,
    RegularReport,
    Report,
    TopReport,
    create_report,
)
from logstats.source_parser import FetchedSource


class StubReport(Report):
    def build_header(self):
        return ""

    def build(self):
        return ["a", "b"]


def test_report_str():
    assert str(StubReport([], ReportRequest(None, 1, False, True))) == "a\nb"


@pytest.fixture
def sample_logs():
    return [
        LogEntry("2026-07-13T13:05:16 ERROR Message"),
        LogEntry("2026-07-13T13:05:17 ERROR Message"),
        LogEntry("2026-07-13T13:05:18 WARNING Message"),
        LogEntry("2026-07-13T13:05:18 WARNING Message"),
        LogEntry("2026-07-13T13:05:19 INFO Message"),
        LogEntry("2026-07-13T14:05:16 ERROR Message"),
        LogEntry("2026-07-14T15:05:16 ERROR Message"),
    ]


@pytest.mark.parametrize(
    "req,expected",
    [
        (
            ReportRequest(None, 1, False, True),
            ["    4 x Error: Message"],
        ),
        (
            ReportRequest(None, 2, False, True),
            [
                "    4 x Error: Message",
                "    2 x Warning: Message",
            ],
        ),
    ],
)
def test_top_report(sample_logs, req: ReportRequest, expected: list[str]):
    assert TopReport(sample_logs, req).build() == expected


@pytest.mark.parametrize(
    "req,expected",
    [
        (
            ReportRequest(None, None, True, True),
            [
                "    2026-07-13 13:00     5",
                "    2026-07-13 14:00     1",
                "    2026-07-14 15:00     1",
            ],
        )
    ],
)
def test_per_hour_report(sample_logs, req: ReportRequest, expected: list[str]):
    assert PerHourReport(sample_logs, req).build() == expected


def test_regular_report(sample_logs):
    result = RegularReport(sample_logs, ReportRequest(None, None, False, True)).build()
    assert len(result) == len(sample_logs)


@pytest.mark.parametrize(
    "req, report_type",
    [
        (ReportRequest(None, 1, False, False), TopReport),
        (ReportRequest(None, None, True, False), PerHourReport),
        (ReportRequest(None, None, False, False), RegularReport),
    ],
)
def test_run_output_correct_report(req: ReportRequest, report_type: type):
    assert type(create_report(FetchedSource([], ""), req)) is report_type


@pytest.mark.parametrize(
    "report, expected",
    [
        (
            PerHourReport([], ReportRequest(None, None, True, True)),
            "All messages per hour:",
        ),
        (TopReport([], ReportRequest(None, 1, False, True)), "Top 1 All messages:"),
        (RegularReport([], ReportRequest(None, None, False, True)), ""),
    ],
)
def test_report_headers(report: Report, expected: str):
    assert report.build_header() == expected
