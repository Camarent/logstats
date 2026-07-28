from abc import ABC, abstractmethod
from collections.abc import Sequence

from logstats.data import LogEntry, ReportRequest, get_name_capitalize
from logstats.per_hour_stats import HourlyStats, build_per_hour
from logstats.source_parser import FetchedSource
from logstats.top_stats import TopStats, build_top


class ReportFormatted(ABC):
    @abstractmethod
    def build_header(self) -> str: ...

    @abstractmethod
    def build(self) -> list[str]: ...

    def __str__(self) -> str:
        return "\n".join([self.build_header(), *self.build()])


class TopReportFormatted(ReportFormatted):
    stats: TopStats

    def __init__(self, stats: TopStats):
        self.stats = stats

    def build_header(self) -> str:
        return f"Top {self.stats.top} {get_name_capitalize(self.stats.level)} messages:"

    def build(self) -> list[str]:
        return [
            f"    {m.count} x {m.level.name.capitalize()}: {m.message}"
            for m in self.stats.messages
        ]


class PerHourReportFormatted(ReportFormatted):
    stats: HourlyStats

    def __init__(self, stats: HourlyStats):
        self.stats = stats

    def build_header(self) -> str:
        return f"{get_name_capitalize(self.stats.level)} messages per hour:"

    def build(self) -> list[str]:
        return [
            f"    {m.timestamp.date()} {m.timestamp.hour:02d}:00     {m.count}"
            for m in self.stats.messages
        ]


class RegularReportFormatted(ReportFormatted):
    logs: Sequence[LogEntry]

    def __init__(self, logs: Sequence[LogEntry]):
        self.logs = logs

    def build_header(self) -> str:
        return ""

    def build(self) -> list[str]:
        return [str(lt) for lt in self.logs]


def create_reports(
    sources: Sequence[FetchedSource], request: ReportRequest
) -> list[ReportFormatted]:
    if request.top is not None:
        tops = build_top(sources, request.level, request.top, request.combined_report)
        return [TopReportFormatted(st) for st in tops]
    elif request.per_hour:
        hourly = build_per_hour(sources, request.level, request.combined_report)
        return [PerHourReportFormatted(st) for st in hourly]
    else:
        return [
            RegularReportFormatted([line for fs in sources for line in fs.log_lines])
        ]
