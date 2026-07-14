from pathlib import Path

from data import LogEntry, LogType, Query
from parser import parse_file
from report import PerHourReport, RegularReport, Report, TopReport


def run(logs: list[LogEntry], query: Query) -> Report:
    if query.top is not None:
        return TopReport(logs, query)
    elif query.per_hour:
        return PerHourReport(logs, query)
    else:
        return RegularReport(logs, query)


def main(filename: Path, level: LogType, top: int, per_hour: bool) -> None:
    query = Query(filename, level, top, per_hour)
    logs = parse_file(query.filename, query.level)
    if len(logs) == 0:
        print("No logs avaiable with the selected filters.")
        return
    report = run(logs, query)
    print(report)
