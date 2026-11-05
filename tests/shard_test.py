from collections import Counter

from logstats.data import LogEntry, LogType
from logstats.shard import from_json, merge, shard_counts, to_json
from logstats.top_stats import compute_top


def _entries(messages: dict[str, int]) -> list[LogEntry]:
    return [
        LogEntry(f"2026-07-13T13:05:16 ERROR {msg}")
        for msg, n in messages.items()
        for _ in range(n)
    ]


def test_roundtrip_json_equals_original():
    entries = [*_entries({"a": 3, "b": 1}), LogEntry("2026-07-13T13:05:16 WARNING b")]
    counter = shard_counts(entries)
    assert from_json(to_json(counter)) == counter


def test_roundtrip_keeps_every_key_untruncated():
    counter = shard_counts(_entries({f"m{i}": i + 1 for i in range(20)}))
    restored = from_json(to_json(counter))
    assert len(restored) == 20
    assert restored == counter


def test_to_json_is_list_of_level_message_count_rows():
    counter = Counter({(LogType.ERROR, "x"): 2})
    assert to_json(counter) == '[[3, "x", 2]]'


def test_empty_counter_roundtrip():
    assert from_json(to_json(Counter())) == Counter()


def test_merge_sums_counts():
    left = shard_counts(_entries({"a": 3, "c": 2}))
    right = shard_counts(_entries({"b": 3, "c": 2}))
    merged = merge([left, right])
    assert merged[(LogType.ERROR, "c")] == 4
    assert merged[(LogType.ERROR, "a")] == 3
    assert merged[(LogType.ERROR, "b")] == 3


def test_merge_top1_differs_from_each_shard_top1():
    left = shard_counts(_entries({"a": 3, "c": 2}))
    right = shard_counts(_entries({"b": 3, "c": 2}))
    assert left.most_common(1)[0][0] == (LogType.ERROR, "a")
    assert right.most_common(1)[0][0] == (LogType.ERROR, "b")

    merged = merge([left, right])
    assert merged.most_common(1)[0][0] == (LogType.ERROR, "c")
    combined = compute_top(
        _entries({"a": 3, "c": 2}) + _entries({"b": 3, "c": 2}),
        "x",
        level=None,
        top=1,
    )
    assert combined.messages[0].message == "c"
