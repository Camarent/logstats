from collections import Counter

from data import LogEntry, Query, get_name_capitalize


class Report:
    logs: list[LogEntry]
    query: Query

    def __init__(self, logs: list[LogEntry], query: Query):
        self.logs = logs
        self.query = query

    def build(self) -> list[str]:
        raise NotImplementedError

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
