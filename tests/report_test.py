import pytest

from logstats.data import LogEntry, ReportRequest
from logstats.per_hour_stats import HourlyStats, compute_per_hour
from logstats.report import Report, format_hourly, format_regular, format_top
from logstats.top_stats import TopStats, compute_top


def test_report_str():
    assert str(Report("app1.log", "head", ["a", "b"])) == "[app1.log] head\na\nb"


def test_report_str_without_header():
    assert str(Report("", "", ["a", "b"])) == "a\nb"


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
    assert format_top(stats).lines == expected


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
    assert format_hourly(stats).lines == expected


def test_regular_report(sample_logs):
    assert len(format_regular(sample_logs).lines) == len(sample_logs)


@pytest.mark.parametrize(
    "report, expected",
    [
        (
            format_hourly(HourlyStats("app1.log", None, 0, [])),
            "[app1.log] All messages per hour:",
        ),
        (
            format_top(TopStats("app1.log", 1, None, 0, [])),
            "[app1.log] Top 1 All messages:",
        ),
        (format_regular([]), ""),
    ],
)
def test_report_headers(report: Report, expected: str):
    assert report.build_header() == expected
