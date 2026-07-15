from pathlib import Path
from unittest.mock import mock_open

import pytest

from logstats.data import LogType
from logstats.parser import parse_file, parse_line


@pytest.mark.parametrize(
    "line,filter",
    [
        ("", None),
        ("\n", None),
        ("Bad Line", None),
        ("Bad Line\n", None),
        (
            "2026-07-13T10:11:08 ERROR Database connection failed: timeout after 30s",
            LogType.WARNING,
        ),
        ("2026-07-13T09:00:00 NOPE hi", None),
        ("not-a-timestamp INFO hello", None),
    ],
)
def test_bad_cases_parse_line(line: str, filter: LogType):
    assert parse_line(line, filter) is None


def test_correctly_remove_newline_parse_line():
    test_line = "2026-07-13T10:11:08 ERROR Message\n"
    assert parse_line(test_line, None).message == "Message"


def test_parse_file(monkeypatch):
    """
    This test is quite advanced and it's more to test Mock then use it in the production.
    """
    contents = """2026-07-13T10:33:19 WARNING Retrying upstream request (attempt 2/3)
2026-07-13T10:52:03 DEBUG Garbage collection freed 128MB
2026-07-13T11:04:27 INFO Shutting down gracefully
2026-07-13T13:05:16 ERROR Database connection failed: timeout after 30s"""
    monkeypatch.setattr(Path, "open", mock_open(read_data=contents))

    result = parse_file(Path("mock.log"), None)
    assert len(result) == 4
    assert result[0].level == LogType.WARNING
