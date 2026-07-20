import logging
from collections.abc import Sequence
from pathlib import Path

from logstats.data import LogEntry, LogType, Query
from logstats.parser import parse_file
from logstats.report import PerHourReport, RegularReport, Report, TopReport

logger = logging.getLogger(__name__)


def run(logs: Sequence[LogEntry], query: Query) -> Report:
    if query.top is not None:
        return TopReport(logs, query)
    elif query.per_hour:
        return PerHourReport(logs, query)
    else:
        return RegularReport(logs, query)


def main(
    filename: Path, level: LogType | None, top: int | None, per_hour: bool
) -> None:
    query = Query(filename, level, top, per_hour)
    logs = parse_file(query.filename, query.level)
    if len(logs) == 0:
        logger.info("No logs available with the selected filters.")
        return
    report = run(logs, query)
    print(report)
