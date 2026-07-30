import pytest

from logstats.data import LogEntry, ReportRequest
from logstats.per_hour_stats import HourlyStats, compute_per_hour
from logstats.report import (
    PerHourReportFormatted,
    RegularReportFormatted,
    ReportFormatted,
    TopReportFormatted,
)
from logstats.top_stats import TopStats, compute_top


class StubReport(ReportFormatted):
    def build_header(self):
        return ""

    def build(self):
        return ["a", "b"]


def test_report_str():
    assert str(StubReport()) == "\na\nb"


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
    assert req.top is not None
    stats = compute_top(sample_logs, "All", level=None, top=req.top)
    assert TopReportFormatted(stats).build() == expected


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
    stats = compute_per_hour(sample_logs, "All", level=None)
    assert PerHourReportFormatted(stats).build() == expected


def test_regular_report(sample_logs):
    result = RegularReportFormatted(sample_logs).build()
    assert len(result) == len(sample_logs)


@pytest.mark.parametrize(
    "report, expected",
    [
        (
            PerHourReportFormatted(HourlyStats("", None, 0, [])),
            "All messages per hour:",
        ),
        (
            TopReportFormatted(TopStats("", 1, None, 0, [])),
            "Top 1 All messages:",
        ),
        (RegularReportFormatted([]), ""),
    ],
)
def test_report_headers(report: ReportFormatted, expected: str):
    assert report.build_header() == expected
