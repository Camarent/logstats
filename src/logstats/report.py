from abc import ABC, abstractmethod
from collections import Counter
from collections.abc import Sequence

from logstats.data import LogEntry, Query, get_name_capitalize


class Report(ABC):
    logs: Sequence[LogEntry]
    query: Query

    def __init__(self, logs: Sequence[LogEntry], query: Query):
        self.logs = logs
        self.query = query

    @abstractmethod
    def build(self) -> list[str]: ...

    def __str__(self) -> str:
        return "\n".join(self.build())


class TopReport(Report):
    def build(self) -> list[str]:
        messages = Counter((e.level, e.message) for e in self.logs)
        scope = get_name_capitalize(self.query.level)
        results = [f"Top {self.query.top} {scope} messages:"]
        for (lvl, msg), n in messages.most_common(self.query.top):
            results.append(f"    {n} x {lvl.name.capitalize()}: {msg}")
        return results


class PerHourReport(Report):
    def build(self) -> list[str]:
        messages = Counter((e.timestamp.date(), e.timestamp.hour) for e in self.logs)
        scope = get_name_capitalize(self.query.level)
        results = [f"{scope} messages per hour:"]
        for (day, hour), n in sorted(messages.items()):
            results.append(f"    {day} {hour:02d}:00     {n}")
        return results


class RegularReport(Report):
    def build(self) -> list[str]:
        return [str(lt) for lt in self.logs]
