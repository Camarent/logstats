import json
from collections import Counter
from collections.abc import Iterable

from logstats.data import LogEntry, LogType

ShardKey = tuple[LogType, str]


def shard_counts(entries: Iterable[LogEntry]) -> Counter[ShardKey]:
    return Counter((e.level, e.message) for e in entries)


def to_json(counter: Counter[ShardKey]) -> str:
    rows = [[level.value, message, n] for (level, message), n in counter.items()]
    return json.dumps(rows)


def from_json(text: str) -> Counter[ShardKey]:
    rows = json.loads(text)
    counter: Counter[ShardKey] = Counter()
    for index, row in enumerate(rows):
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError(f"row {index}: expected [level, message, count]")
        level_value, message, n = row
        if not isinstance(message, str):
            raise ValueError(f"row {index}: message must be str")
        if not isinstance(n, int) or isinstance(n, bool) or n < 0:
            raise ValueError(f"row {index}: count must be int >= 0")
        counter[(LogType(level_value), message)] += n
    return counter


def merge(counters: Iterable[Counter[ShardKey]]) -> Counter[ShardKey]:
    total: Counter[ShardKey] = Counter()
    for counter in counters:
        total.update(counter)
    return total
