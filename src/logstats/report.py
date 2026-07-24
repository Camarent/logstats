from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Sequence

from logstats.data import LogEntry, ReportRequest, get_name_capitalize
from logstats.source_parser import FetchedSource


class Report(ABC):
    logs: Sequence[LogEntry]
    request: ReportRequest

    def __init__(self, logs: Sequence[LogEntry], query: ReportRequest):
        self.logs = logs
        self.request = query

    @abstractmethod
    def build_header(self) -> str: ...

    @abstractmethod
    def build(self) -> list[str]: ...

    def __str__(self) -> str:
        return self.build_header() + "\n".join(self.build())


class TopReport(Report):
    def build_header(self) -> str:
        return f"Top {self.request.top} {get_name_capitalize(self.request.level)} messages:"

    def build(self) -> list[str]:
        messages = Counter((e.level, e.message) for e in self.logs)
        return [
            f"    {n} x {lvl.name.capitalize()}: {msg}"
            for (lvl, msg), n in messages.most_common(self.request.top)
        ]


class PerHourReport(Report):
    def build_header(self) -> str:
        return f"{get_name_capitalize(self.request.level)} messages per hour:"

    def build(self) -> list[str]:
        messages = Counter((e.timestamp.date(), e.timestamp.hour) for e in self.logs)
        return [
            f"    {day} {hour:02d}:00     {n}"
            for (day, hour), n in sorted(messages.items())
        ]


class RegularReport(Report):
    def build_header(self) -> str:
        return ""

    def build(self) -> list[str]:
        return [str(lt) for lt in self.logs]


def create_report(source: FetchedSource, query: ReportRequest) -> Report:
    if query.top is not None:
        return TopReport(source.log_lines, query)
    elif query.per_hour:
        return PerHourReport(source.log_lines, query)
    else:
        return RegularReport(source.log_lines, query)
