from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from logstats.data import LogEntry, get_name_capitalize
from logstats.per_hour_stats import HourlyStats
from logstats.top_stats import TopStats


class ReportFormatted(ABC):
    @abstractmethod
    def build_header(self) -> str: ...

    @abstractmethod
    def build(self) -> list[str]: ...

    def __str__(self) -> str:
        return "\n".join([self.build_header(), *self.build()])


@dataclass
class TopReportFormatted(ReportFormatted):
    stats: TopStats

    def build_header(self) -> str:
        return f"Top {self.stats.top} {get_name_capitalize(self.stats.level)} messages:"

    def build(self) -> list[str]:
        return [
            f"    {m.count} x {m.level.name.capitalize()}: {m.message}"
            for m in self.stats.messages
        ]


@dataclass
class PerHourReportFormatted(ReportFormatted):
    stats: HourlyStats

    def build_header(self) -> str:
        return f"{get_name_capitalize(self.stats.level)} messages per hour:"

    def build(self) -> list[str]:
        return [
            f"    {m.timestamp.date()} {m.timestamp.hour:02d}:00     {m.count}"
            for m in self.stats.messages
        ]


@dataclass
class RegularReportFormatted(ReportFormatted):
    logs: Sequence[LogEntry]

    def build_header(self) -> str:
        return ""

    def build(self) -> list[str]:
        return [str(lt) for lt in self.logs]
