from datetime import datetime

import pytest

from logstats.data import InvalidLogFormat, LogEntry, LogType, get_name_capitalize


@pytest.mark.parametrize(
    "test_input,expected",
    [(LogType.ERROR, "Error"), (LogType.DEBUG, "Debug"), (None, "All")],
)
def test_get_name_capitalize(test_input, expected):
    assert get_name_capitalize(test_input) == expected


def test_produce_log_entry():
    test_line = "2026-07-13T10:33:19 WARNING Retrying upstream request (attempt 2/3)"
    entry = LogEntry(test_line)
    assert entry.message == "Retrying upstream request (attempt 2/3)"
    assert entry.level == LogType.WARNING
    assert entry.timestamp == datetime.fromisoformat("2026-07-13T10:33:19")


@pytest.mark.parametrize(
    "bad_line",
    [
        "",
        "Broken Line",
        "2026-07-13T10:33:19 WARNING ",
    ],
)
def test_invalid_format(bad_line: str):
    with pytest.raises(InvalidLogFormat):
        LogEntry(bad_line)


@pytest.mark.parametrize(
    "bad_line",
    [
        "10/01/2020T10:33:19 WARNING Retrying upstream request (attempt 2/3)",
        "2026-07-13T10:33:19 SUPER_ERROR Retrying upstream request (attempt 2/3)",
    ],
)
def test_invalid_enum_or_data_formats(bad_line: str):
    with pytest.raises((ValueError, KeyError)):
        LogEntry(bad_line)
