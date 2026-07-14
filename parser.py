from pathlib import Path

from data import InvalidLogFormat, LogEntry, LogType


def parse_file(filename: Path, level: LogType) -> list[LogEntry]:
    with filename.open("rt") as f:
        return [entry for lt in f if (entry := parse_line(lt, level)) is not None]


def parse_line(line: str, level: LogType) -> LogEntry | None:
    try:
        entry = LogEntry(line.rstrip("\n"))
        return entry if level is None or entry.level == level else None
    except InvalidLogFormat as ex:
        print(ex)
    except (ValueError, KeyError) as gex:
        print(f'Exception "{gex}" was raised for line "{line}"')
