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
    for level_value, message, n in rows:
        counter[(LogType(level_value), message)] += n
    return counter


def merge(counters: Iterable[Counter[ShardKey]]) -> Counter[ShardKey]:
    total: Counter[ShardKey] = Counter()
    for counter in counters:
        total.update(counter)
    return total
