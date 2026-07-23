from pathlib import Path

import pytest

from logstats.data import LogEntry, Query
from logstats.report import PerHourReport, RegularReport, Report, TopReport


class StubReport(Report):
    def build(self):
        return ["a", "b"]


def test_report_str():
    assert str(StubReport([], Query(Path(""), None, 1, False))) == "a\nb"


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
    "query,expected",
    [
        (
            Query(Path(""), None, 1, False),
            ["Top 1 All messages:", "    4 x Error: Message"],
        ),
        (
            Query(Path(""), None, 2, False),
            [
                "Top 2 All messages:",
                "    4 x Error: Message",
                "    2 x Warning: Message",
            ],
        ),
    ],
)
def test_top_report(sample_logs, query: Query, expected: list[str]):
    assert TopReport(sample_logs, query).build() == expected


@pytest.mark.parametrize(
    "query,expected",
    [
        (
            Query(Path(""), None, None, True),
            [
                "All messages per hour:",
                "    2026-07-13 13:00     5",
                "    2026-07-13 14:00     1",
                "    2026-07-14 15:00     1",
            ],
        )
    ],
)
def test_per_hour_report(sample_logs, query: Query, expected: list[str]):
    assert PerHourReport(sample_logs, query).build() == expected


def test_regular_report(sample_logs):
    result = RegularReport(sample_logs, Query(Path(""), None, None, False)).build()
    assert len(result) == len(sample_logs)
