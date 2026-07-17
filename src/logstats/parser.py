import logging
from pathlib import Path

from logstats.data import InvalidLogFormat, LogEntry, LogType

logger = logging.getLogger("logstats_parser")


def parse_file(filename: Path, level: LogType | None) -> list[LogEntry]:
    with filename.open("rt") as f:
        return [entry for lt in f if (entry := parse_line(lt, level)) is not None]


def parse_line(line: str, level: LogType | None) -> LogEntry | None:
    try:
        entry = LogEntry(line.rstrip("\n"))
        return entry if level is None or entry.level == level else None
    except InvalidLogFormat as ex:
        logger.warning(ex)
    except (ValueError, KeyError) as gex:
        logger.warning(f'Exception "{gex}" was raised for line "{line}"')
    return None
