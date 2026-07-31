from collections.abc import Sequence
from dataclasses import dataclass

from logstats.data import LogEntry, level_label
from logstats.per_hour_stats import HourlyStats
from logstats.top_stats import TopStats


@dataclass(frozen=True)
class Report:
    source: str
    header: str
    lines: list[str]

    def build_header(self) -> str:
        return f"[{self.source}] {self.header}" if self.source else self.header

    def __str__(self) -> str:
        header = self.build_header()
        return "\n".join([header, *self.lines] if header else self.lines)


def format_top(stats: TopStats) -> Report:
    return Report(
        stats.source,
        f"Top {stats.top} {level_label(stats.level)} messages:",
        [
            f"    {m.count} x {m.level.name.capitalize()}: {m.message}"
            for m in stats.messages
        ],
    )


def format_hourly(stats: HourlyStats) -> Report:
    return Report(
        stats.source,
        f"{level_label(stats.level)} messages per hour:",
        [
            f"    {m.timestamp.date()} {m.timestamp.hour:02d}:00     {m.count}"
            for m in stats.messages
        ],
    )


def format_regular(stats: Sequence[LogEntry]) -> Report:
    return Report("", "", [str(lt) for lt in stats])
